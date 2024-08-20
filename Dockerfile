FROM amazonlinux:2017.09.0.20170930
RUN yum -y install vim httpd python27 python27-devel python27-pip wget gcc gcc-c++ subversion make uuid libuuid-devel httpd-devel mysql-devel
RUN wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.15.tar.gz && tar -xvf 4.5.15.tar.gz && cd mod_wsgi-4.5.15 && ./configure --with-python=/usr/bin/python27 && make; make install && cd .. && rm -r mod_wsgi-4.5.15 4.5.15.tar.gz
# configure settings.py as part of build process
COPY docker_config/vhosts.conf /etc/httpd/conf.d/
COPY docker_config/wsgi.conf /etc/httpd/conf.d/
COPY dependencies.list /etc/
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip install --ignore-installed --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r /etc/dependencies.list && rm /etc/dependencies.list
# update this to pipe to AWS log later
RUN mkdir /var/log/api && chown apache:apache /var/log/api
RUN echo "ServerName 172.*" >> /etc/httpd/conf/httpd.conf
EXPOSE 80
CMD ["/usr/sbin/httpd","-D","FOREGROUND"]