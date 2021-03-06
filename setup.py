#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
  name="pyapns",
  version="0.3.2",
  description="A universal Apple Push Notification Service (APNS) provider.",
  long_description="""
Features:

    * XML-RPC Based, works with any client in any language
    * Native Python API with Django and Pylons support
    * Scalable, fast and easy to distribute behind a proxy
    * Based on Twisted
    * Multi-application and dual environment support
    * Simplified feedback interface

pyapns is an APNS provider that you install on your server and access through XML-RPC.
To install you will need Python, Twisted_ and pyOpenSSL_. It's also recommended to 
install `python-epoll`_ for best performance (if epoll is not available, like on 
Mac OS X, you may want to use another library, like `py-kqueue`_. If you like 
easy_install try (it should take care of the dependancies for you)::

    $ sudo easy_install pyapns

pyapns is a service that runs persistently on your machine. To start it::

    $ twistd -r epoll web --class=pyapns.server.APNSServer --port=7077

To get started right away, use the included client::

    $ python
    >>> from pyapns import configure, provision, notify
    >>> configure({'HOST': 'http://localhost:7077/'})
    >>> provision('myapp', open('cert.pem').read(), 'sandbox')
    >>> notify('myapp', 'hexlified_token_str', {'aps':{'alert': 'Hello!'}})

The Multi-Application Model
---------------------------
pyapns supports multiple applications. Before pyapns can send notifications,
you must first provision the application with an Application ID, the environment
(either 'sandbox' or 'production') and the certificate file. The `provision`
method takes 4 arguments, `app_id`, `path_to_cert_or_cert`, `environment`
and `timeout`. A connection is kept alive for each application provisioned
for the fastest service possible. The application ID is an arbitrary
identifier and is not used in communication with the APNS servers.

When a connection can not be made within the specified `timeout` a timeout 
error will be thrown by the server. This usually indicates that the wrong 
[type of] certification file is being used, a blocked port or the wrong environment.

Sending Notifications
---------------------
Calling `notify` will send the message immediately if a connection is already
established. The first notification may be delayed a second while the server 
connects. ``notify`` takes ``app_id``, ``token_or_token_list`` and 
`notification_or_notification_list`. Multiple notifications can be batched 
for better performance by using paired arrays of token/notifications. When 
performing batched notifications, the token and notification arrays must be 
exactly the same length.

The full notification dictionary must be included as the notification::

    {'aps': {
        'sound': 'flynn.caf',
        'badge': 0,
        'message': 'Hello from pyapns :)'
      }
    } # etc...

Retrieving Inactive Tokens
--------------------------
Call `feedback` with the `app_id`. A list of tuples will be retrieved from the 
APNS server that it deems inactive. These are returned as a list of 2-element 
lists with a `Datetime` object and the token string.

XML-RPC Methods
---------------

``provision``
-------------

::

      Arguments
          app_id        String            the application id for the provided
                                          certification
          cert          String            a path to a .pem file or the a
                                          string with the entie file
          environment   String            the APNS server to use - either
                                          'production' or 'sandbox'
          timeout       Integer           timeout for connection attempts to
                                          the APS servers
      Returns
          None

``notify``
----------

::

      Arguments
          app_id        String            the application id to send the
                                          message to
          tokens        String or Array   an Array of tokens or a single
                                          token string
          notifications String or Array   an Array of notification
                                          dictionaries or a single
                                          notification dictionary

      Returns
          None

``feedback``
------------

::

      Arguments
          app_id        String            the application id to retrieve
                                          retrieve feedback for

      Returns
          Array(Array(Datetime(time_expired), String(token)), ...)


The Python API
--------------
pyapns also provides a Python API that makes the use of pyapns even simpler. 
The Python API must be configured before use but configuration files make it easier.
The pyapns `client` module currently supports configuration from Django settings and
Pylons config. To configure using Django, the following must be present in  
your settings file::

    PYAPNS_CONFIG = {
      'HOST': 'http://localhost:8077/',
      'TIMEOUT': 15,                    # OPTIONAL, host timeout in seconds
      'INITIAL': [                      # OPTIONAL, see below
        ('craigsfish', '/home/samsutch/craigsfish/apscert.pem', 'sandbox'),
      ]
    }

Optionally, with Django settings, you can skip manual provisioning by including a 
list of `(name, path, environment)` tuples that are guaranteed to be provisioned 
by the time you call `notify` or `feedback`.

Configuring for pylons is just as simple, but automatic provisioning isn't 
possible, in your configuration file include::

    pyapns_host = http://localhost:8077/
    pyapns_timeout = 15

For explanations of the configuration variables see the docs for 
`pyapns.client.configure`.

Each of these functions can be called synchronously and asynchronously. To make 
them perform asynchronously simply supply a callback. The request will then be
made in another thread and callback with the results. When calling asynchronously 
no value will be returned::

    def got_feedback(tuples):
      trim_inactive_tokens(tuples)
    feedback('myapp', callback=got_feedback)

``pyapns.client.configure(opts)``
---------------------------------

::

    Takes a dictionary of options and configures the client. 
    Currently configurable options are 'HOST', 'TIMEOUT' and 'INITIAL' the latter
    of which is only read once.

    Config Options:
        HOST        - A full host name with port, ending with a forward slash
        TIMEOUT     - An integer specifying how many seconds to timeout a
                      connection to the pyapns server (prevents deadlocking
                      the parent thread).
        INITIAL     - A List of tuples to be supplied to provision when
                      the first configuration happens.

``pyapns.client.provision(app_id, path_to_cert_or_cert, environment, timeout=15, callback=None)``
-------------------------------------------------------------------------------------------------

::

    Provisions the app_id and initializes a connection to the APNS server.
    Multiple calls to this function will be ignored by the pyapns daemon
    but are still sent so pick a good place to provision your apps, optimally
    once.

    Arguments:
        app_id                 the app_id to provision for APNS
        path_to_cert_or_cert   absolute path to the APNS SSL cert or a 
                               string containing the .pem file
        environment            either 'sandbox' or 'production'
        timeout                number of seconds to timeout connection
                               attempts to the APPLE APS SERVER
        callback               a callback to be executed when done
    Returns:
        None

``pyapns.client.notify(app_id, tokens, notifications, callback=None)``
----------------------------------------------------------------------

::

    Sends push notifications to the APNS server. Multiple 
    notifications can be sent by sending pairing the token/notification
    arguments in lists [token1, token2], [notification1, notification2].

    Arguments:
        app_id                 provisioned app_id to send to
        tokens                 token to send the notification or a 
                               list of tokens
        notifications          notification dicts or a list of notifications
        callback               a callback to be executed when done
      Returns:
          None

``pyapns.client.feedback(app_id, callback=None)``
-------------------------------------------------

::

    Retrieves a list of inactive tokens from the APNS server and the times
    it thinks they went inactive.

    Arguments:
        app_id                 the app_id to query
    Returns:
        Feedback tuples like [(datetime_expired, token_str), ...]

.. _Twisted: http://pypi.python.org/pypi/Twisted
.. _pyOpenSSL: http://pypi.python.org/pypi/pyOpenSSL
.. _python-epoll: http://pypi.python.org/pypi/python-epoll/
.. _py-kqueue: http://pypi.python.org/pypi/py-kqueue/2.0.1

""",
  author="Samuel Sutch",
  author_email="samuraiblog@gmail.com",
  license="MIT",
  url="http://github.com/samuraisam/pyapns/tree/master",
  download_url="http://github.com/samuraisam/pyapns/tree/master",
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'],
  packages=['pyapns'],
  package_data={},
  install_requires=['Twisted>=8.2.0', 'pyOpenSSL>=0.10']
  )
