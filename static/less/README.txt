http://stackoverflow.com/questions/7942277/less-css-minimal-setup-failure
for local file based development:
$ google-chrome -allow-file-access-from-files
$ chromium-browser --allow-file-access-from-files &
(firefox works as is)


*2013.03.22 12:57:34 
it is possible to run less in the browser (client side):
http://lesscss.org/#usage

      less = {
        env: "development", // or "production"
        poll: 1000,    when in watch mode, time in ms between polls
      };


to enable watch mode, append '#!watch' to the url
or run less.watch() from the console



to compile less to css:
(which you should do eventually for production)
(and may be useful when chrome was not started correctly)
make sure you have npm
which npm
if you don't have it, install node
http://nodejs.org/download/
(sudo apt-get install npm)

then install less for node:
sudo npm install -g less

lessc style.less > ../css/style.css

may need to reference nodejs instead of just node on xubuntu
sudo vi /usr/local/bin/lessc
