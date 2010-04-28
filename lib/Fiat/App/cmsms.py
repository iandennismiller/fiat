from Fiat.Base.App import BaseApp
from Fiat.Core.Utils import loggable
import os, distutils, commands, shutil, string, re, mechanize

class cmsms(BaseApp):

    #def __init__(self, Instance, db_type, config_dict):
    def __init__(self, Instance, config_dict):
        self.meta = {
            "type": "cmsms",
            "version": Instance.Project.Exec.config['cmsms_version'],
            }

        self.config_parse = {
            'regexp': r'\$config\[\'%s\'\]\s*=\s*\'(.*?)\';',
            'db_host': r'db_hostname',
            'db_user': r'db_username',
            'db_pass': r'db_password',
            'db_name': r'db_name',
            }

        #super(cmsms, self).__init__(Instance, db_type, config_dict)
        super(cmsms, self).__init__(Instance, config_dict)

        self.Exec.register_task(name="cmsms.start.install", args=0, help="install cmsms", function=self.install_start)
        self.Exec.register_task(name="cmsms.start.upgrade", args=0, help="begin upgrading cmsms version", function=self.upgrade_start)
        self.Exec.register_task(name="cmsms.finish", args=0, help="finish cmsms upgrade or install", function=self.upgrade_finish)

        self.Exec.register_task(name="cmsms.uploads.checkin", args=0, help="check in CMSMS uploads", function=self.checkin_uploads)
        self.Exec.register_task(name="cmsms.theme", args=0, help="deploy cmsms theme", function=self.deploy_theme)
        self.Exec.register_task(name="cmsms.cache", args=0, help="clear the cmsms cache", function=self.clear_cache)

    @loggable
    def build(self, dest="cms"):

        self.Exec.Utils.cp_build("var/cmsms", dest)
        self.Exec.Utils.cp_build("var/uploads", "%s/uploads" % dest)
        self.Exec.Utils.cp_build("var/highriseweb/admin", "%s/admin" % dest)

        theme_dict = self.Project.cmsms_theme()
        theme_prefix = theme_dict['prefix']
        theme_name = os.path.split(theme_prefix)[1]

        theme_from = os.path.join(theme_prefix, "public_html")
        theme_to = os.path.join(dest, 'theme', theme_name)

        try:
            os.mkdir(os.path.join(self.Project.config['build_path'], dest, 'theme'))
        except OSError:
            pass

        self.Exec.Utils.cp_build(theme_from, theme_to)

    @loggable
    def install_start(self):
        self.upgrade_start(install=True)

    @loggable
    def upgrade_start(self, install=False):
        if install:
            self.DB.create_db()
        else:
            self.DB.checkin_database()
            self.checkin_uploads()
        
        install_path = os.path.join(self.Project.config['make_path'], "var", "cmsms")
        
        self.Exec.Utils.unpack_tarball("cmsms", self.Exec.config["cmsms_version"], install_path)
        shutil.rmtree(os.path.join(install_path, "doc"))
        os.remove(os.path.join(install_path, "tmp/cache/SITEDOWN"))

        self.Project.clean()
        self.Project.build()
        self.Project.deploy()
        
        ssh_cmd = "chmod 666 %(path)s/cms/config.php; chmod 777 %(path)s/cms/modules" % \
            {"path": self.Instance.Host.config["install_path"]}
        
        self.Instance.Host.ssh(cmd=ssh_cmd)
        
        if install:
            os.system("open %s/install/install.php" % self.config["url"])
        else:
            os.system("open %s/install/upgrade.php" % self.config["url"])

    @loggable
    def upgrade_finish(self):
        install_path = os.path.join(self.Project.config['make_path'], "var", "cmsms")

        self.Project.clean()
        try:
            shutil.rmtree(os.path.join(install_path, "install"))
        except OSError:
            self.Exec.logger.warn("unable to remove path %s" % os.path.join(install_path, "install"))

        ssh_cmd = "chmod 644 %(path)s/cms/config.php; chmod 775 %(path)s/cms/modules; rm -rf %(path)s/cms/install" % \
            {"path": self.Instance.Host.config["install_path"]}

        self.Instance.Host.ssh(cmd=ssh_cmd)

        self.Instance.Host.scp_from("%s/cms/config.php" % self.Instance.Host.config["install_path"])

        os.system("sdiff %s %s/tmp/config.php" % \
            (self.config["config_filename"], self.Project.config["make_path"]))

        self.Exec.logger.info("If config is acceptable, 'cp %s/tmp/config.php %s'" % \
                (self.Project.config["make_path"], self.config["config_filename"]))

    @loggable
    def checkin_uploads(self):
        source = os.path.join(self.Instance.Host.config['install_path'], "cms/uploads/")
        destination = os.path.join(self.Project.config['make_path'], "var/uploads")
        
        self.Instance.Host.rsync_down(source, destination)
        
    @loggable
    def deploy_theme(self):
        theme_dict = self.Project.cmsms_theme()

        theme_prefix = theme_dict['prefix']
        theme_css = theme_dict['css']
        theme_template = theme_dict['template'] 
        theme_sql_filename = os.path.join(self.Project.config['make_path'], "tmp", "cmsms_theme.sql")

        theme_sql = 'lock tables `cms_css` WRITE;\n'

        for css_id in theme_css.keys():
            source_file = os.path.join(self.Project.config['make_path'], theme_prefix, theme_css[css_id])
            self.Exec.logger.info('read file %s', source_file)  
            source_content = self.DB.escape(string.join(open(source_file).readlines()))
            theme_sql = theme_sql + "update `cms_css` set css_text = '%s' where css_id=%s;\n" % (source_content, css_id)

        theme_sql = theme_sql + "unlock tables;\n" + "lock tables `cms_templates` WRITE;\n"

        for template_id in theme_template.keys():
            source_file = os.path.join(self.Project.config['make_path'], theme_prefix, theme_template[template_id])
            self.Exec.logger.info('read file %s', source_file)
            source_content = self.DB.escape(string.join(open(source_file).readlines()))
            theme_sql = theme_sql + "update `cms_templates` set template_content = '%s' where template_id=%s;\n" % \
                (source_content, template_id)

        theme_sql = theme_sql + "unlock tables;"

        theme_sql_file = open(theme_sql_filename, 'w')
        theme_sql_file.writelines(theme_sql)
        theme_sql_file.close()

        self.DB.deploy_and_import(
            local_path = os.path.join(self.Project.config['make_path'], "tmp"),
            filename = "cmsms_theme.sql", 
            remote_temp_path = self.Instance.Host.config['scratch_path']
            )

        self.clear_cache()

    @loggable
    def clear_cache(self):
        br = mechanize.Browser()
        
        #cookiefile = "/tmp/cj.txt"
        #cj = mechanize.LWPCookieJar(cookiefile)
        #if not os.path.isfile(cookiefile):
        #    cj.save()
        #cj.load()        
        #br.set_cookiejar(cj)
        
        br.open("%s/admin/siteprefs.php" % self.config["url"])

        if br.title() == "CMS Login":
            br.form = br.forms().next()
            br["username"] = self.config["admin_user"]
            br["password"] = self.config["admin_pass"]
            response = br.submit()
            if br.title() == "CMS Login":
                self.Exec.logger.error("unable log in")
                return
            else:
                self.Exec.logger.info("successfully logged in")
                link = br.links(url_regex="siteprefs").next()
                #cj.save()
                br.follow_link(link)
        
        if not re.search(r"Global.*Settings", br.title()):
            self.Exec.logger.error("unable to retrieve siteprefs.php, got %s instead" % br.title())
            return
        else:
            br.form = br.forms().next()
            response = br.submit("clearcache")
            if re.search(r"Cache Cleared", response.read()):
                self.Exec.logger.info("successfully cleared cache")
            else:
                self.Exec.logger.error("problem clearing the cache")

