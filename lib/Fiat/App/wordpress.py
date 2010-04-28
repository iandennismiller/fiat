from Fiat.Base.App import BaseApp
from Fiat.Core.Utils import loggable, copy_directory
import os, distutils, shutil

class wordpress(BaseApp):

    def __init__(self, Instance, config_dict):
        self.meta = {
            "type": "wordpress",
            "version": Instance.Project.Exec.config['wordpress_version'],
            }

        self.config_parse = {
            'regexp': r'\s*define\(\'%s\'\s*,\s*\'(.*?)\'\);',
            'db_host': r'DB_HOST',
            'db_user': r'DB_USER',
            'db_pass': r'DB_PASSWORD',
            'db_name': r'DB_NAME',
        }

        self.plugins = [
            "addquicktag",
            "add-to-any",
            "akismet",
            "best-foot-forward",
            "configurable-tag-cloud-widget",
            "disqus-comment-system",
            "php-code-widget",
            "get-recent-comments",
            "google-news-sitemap-generator",
            "google-sitemap-generator",
            "organize-series",
            "search-unleashed",
            "seo-automatic-links",
            "wordpresscom-popular-posts"
            "stats",
            "wp-auto-tagger",
            "wp-cache",
            "wp-polls",
            "yet-another-related-posts-plugin",
            "json-feed",
        ]
        
        self.plugin_base_url = "http://wordpress.org/extend/plugins"

        super(wordpress, self).__init__(Instance, config_dict)

        self.Exec.register_task(name="wordpress.start.upgrade", args=0, help="start upgrading wordpress src", function=self.upgrade_start)
        self.Exec.register_task(name="wordpress.start.install", args=0, help="install wordpress src", function=self.install_start)
        self.Exec.register_task(name="wordpress.uploads.checkin", args=0, help="check in wp uploads", function=self.checkin_uploads)
        self.Exec.register_task(name="wordpress.update.plugins", args=0, help="update wordpress plugins", function=self.update_plugins)
        self.Exec.register_task(name="wordpress.upgrade.plugins", args=0, help="upgrade wordpress plugins", function=self.upgrade_global_plugins)

    @loggable
    def update_plugins(self):
        for plugin in self.config['plugins']:
            self.Exec.logger.debug("updating %s" % plugin)
            source = os.path.join(self.Exec.config['wp_plugin_path'], plugin)
            dest = os.path.join(self.Project.config['make_path'], "var", "wp_plugins", plugin)
            self.Exec.logger.debug("%s to %s" % (source, dest))
            copy_directory(source, dest)

    @loggable
    def upgrade_global_plugins(self):
        for plugin in self.plugins:
            self.Exec.logger.debug("global upgrade on %s" % plugin)
            cmd = """
            export FIATPLUGINS='/usr/local/var/fiat/wordpress'
            export PLUGIN=$1
            export ZIPFILE=`curl -s http://wordpress.org/extend/plugins/$PLUGIN/ | \
            grep http://downloads.wordpress.org/plugin/ | \
            awk '{split($0, a, "'"'"'"); print a[2];}'`

            wget $ZIPFILE -O $FIATPLUGINS/plugin.zip
            unzip -o -d $FIATPLUGINS $FIATPLUGINS/plugin.zip
            rm $FIATPLUGINS/plugin.zip
            """
            # TODO: integrate this
            #os.system("wp_plugin.sh %s" % plugin)

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

        install_path = os.path.join(self.Project.config['make_path'], "var", "wordpress")
        self.Exec.Utils.unpack_tarball("wordpress", self.Exec.config["wordpress_version"], install_path)

        os.remove(os.path.join(install_path, "license.txt"))
        os.remove(os.path.join(install_path, "readme.html"))
        os.remove(os.path.join(install_path, "wp-config-sample.php"))

        if not install:
            shutil.rmtree(os.path.join(install_path, "wp-content/plugins"))
            shutil.rmtree(os.path.join(install_path, "wp-content/themes"))

        self.Project.clean()
        self.Project.build()
        self.Project.simulate()
        
        confirmation = raw_input("Continue with deploy? (must type 'yes'): ")
        if confirmation != 'yes':
            return
        self.Exec.logger.info("continuing...")
        self.Project.deploy()
        
        #ssh_cmd = "chmod 666 %(path)s/cms/config.php; chmod 777 %(path)s/cms/modules" % \
        #    {"path": self.Instance.Host.config["install_path"]}
        
        #ssh_cmd = "ln -s /f1/content/rtfa/public/wp-content/plugins/wp-cache/wp-cache-phase1.php /home/public/wp-content/advanced-cache.php; " + \
        #	"chgrp web /home/public/wp-admin/*.php"
        
        #self.Instance.Host.ssh(cmd=ssh_cmd)
        
        if install:
            os.system("open %s/wp-admin" % self.config["url"])
        else:
            os.system("open %s/wp-admin/upgrade.php" % self.config["url"])

    @loggable
    def build(self, dest="blog"):
        self.Exec.Utils.cp_build("var/wordpress", dest)
        self.Exec.Utils.cp_build("var/wp_uploads", os.path.join(dest, "wp-content/uploads"))
        self.Exec.Utils.cp_build("var/wp_plugins", os.path.join(dest, "wp-content/plugins"))
        self.Exec.Utils.cp_build("src/wp-content", os.path.join(dest, "wp-content"))
        
    @loggable
    def checkin_uploads(self):
        if 'remote_path' in self.config:
            source = os.path.join(self.Instance.Host.config['install_path'], self.config['remote_path'], "wp-content/uploads/")
        else:
            source = os.path.join(self.Instance.Host.config['install_path'], "wp-content/uploads/")
            
        destination = os.path.join(self.Project.config['make_path'], "var/wp_uploads")
        self.Instance.Host.rsync_down(source, destination)

