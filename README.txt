GoMobile is a Plone add-on product to turn Plone to converged web and mobile content management system. 
It aims to be the leading open source solution for mobile and converged content management.
This is achieved by not making compromises on mobile site usability. 

.. contents:: :depth: 2

.. image:: http://plonegomobile.googlecode.com/svn/trunk/gomobile/gomobile.mobile/docs/frontpage.png
   :align: right
   :alt: PloneGoMobile screenshot
   
Features
--------

Note: GoMobile is still under development. Some of these features might require extra work to 
be enabled in your configuration.

* Automatically reformat pages and images suitable for mobile consumption.

* Degenerate gracefully when viewing the pages on less powerful mobile phones (other than webkit based browser)

* Manage web and mobile content from the same user interface.

* Mobile phone preview option for pages in the admin interface.

* Categorize site sections belonging to web, mobile or both (gomobile.convergence product)

* Possible to use same URLs for web and mobile content. This way pages are displayed correctly
  whether the user opens them from his web browser or mobile browser. Very handy for outgoing links in
  email.
  
* Big folder navigation and link buttons for touch screen displays to make the mobile site finger friendly.

* Superious handset database support, sourcing information from multiple handset databases.

* Enable and disable site features depending on whether the handset supports them (location based services, downloadable ringtones, downloadable widgets).

* Built on Plone and Zope component architecture to make the product extensible, configurable and future proof.
  
* Upload video files and they will be automatically transcoded suitable for different web and mobile platforms (commercial add on service)


Requirements
------------

* `Plone <http://plone.org>`_ 3.2 or later

* This product has been tested both on vanilla Plone and `Repoze <http://www.repoze.org>`_ set ups
  
Installation
------------

External Set up
===============

Out-of-the-box setup needs special DNS set-up to work correctly.

- There are three different request types: web, mobile and preview

- Different domain names are used to identify the request type

- URI stays same

Edit your /etc/hosts and add line::

	127.0.0.1 mobi.localhost web.localhost preview.localhost
	
Optional: It is possible to configure the server to use only single domain name. In this case, 
mobile sessions are identified by user agent sniffing and preview requests are identified by a path prefix.


buildout.cfg
============

Installation of GoMobile source codes is buildout recipe based.

Source code can be checked out from `Google Code <http://code.google.com/p/plonegomobile/source/checkout>`_.

Example configuration below::

	# Add additional eggs here
	eggs = 
		archetypes.schemaextender
		gomobile.imageinfo
		gomobile.mobile
		gomobile.convergence
	
	# These are direct SVN trunk checkouts
	develop =
	        ../workspace/gomobile/gomobile.imageinfo
	        ../workspace/gomobile/gomobile.mobile
	        ../workspace/gomobile/gomobile.convergence

	# If you want to register ZCML slugs for any packages, list them here.
	# e.g. zcml = my.package my.other.package
	zcml = 
		archetypes.schemaextender
		gomobile.imageinfo
		gomobile.mobile
		gomobile.convergence
	       
	       
Add on product installers
=========================

Run add on product installers for

* Plone Mobile

* Mobile content convergence (only needed if you indent to use your site to serve both web and mobile content)

Site specific settings
======================

Site specific settings can be found in ZMI. Go portal_properties -> mobile_properties.

See gomobile.mobile/profiles/default/propertiestool.xml for settings descriptions.

Mobile support
--------------

The product has been tested with 

* iPhone

* Various Nokia Series 40 (non-webkit browsers)

* Various Nokia Series 60 models

* BlackPerry models

Usage
-----

To view web site version, go `http://web.localhost <http://web.localhost>`_.

To view mobile site version, go `http://mobi.localhost <http://mobi.localhost>`_.

Portlets
========


The following new portlets are available:

* Mobile preview portlet: render the current page in mobile phone mock up. This generates preview request
  to the site in pop-up iframe.

* Content medias portlet: allow to choose in which medias the content appears: web, mobile, both or 
  use the parent folder setting.

.. image:: http://plonegomobile.googlecode.com/svn/trunk/gomobile/gomobile.mobile/docs/portlets.png
   :alt: Portlets examples
    

Sitemap
=======

Sitemap has been enhanced to show content media and content language for the site administrators. 

.. image:: http://plonegomobile.googlecode.com/svn/trunk/gomobile/gomobile.mobile/docs/sitemap.png
   :alt: Sitemap example

Extended schema
===============

All Plone content types will be retrofitted with the following new fields

* *contentMedia*: convergence options - whether the content should appear in web, mobile or both. This
  setting can be inherited from parent levels. Usually you do not wish to query contentMedia directly,
  instead use gomobile.convergence.ConvergedMediaFilter utility functions.
  
* *mobileFolderListing*: Show mobile specific folder listing for this content [deprecated].

Mobile request discriminating
=============================

gomobile.mobile.discriminator contains an utility which categorizes the incoming HTTP requests to web, mobile and preview requests.

By default, this uses domain name based policy. You can override this to use user agent based policy or cookie based policy.

Note that monkey patching hacks are used to set subdomain cookie: Plone login is valid for web.localhost, mobi.localhost
and preview.localhost domains. If you use ZMI login this does not work.

Mobile theme layer
==================

If discriminator detects a mobile or preview request mobile theme is activated.
This is a normal Plone theme, identified by its name.

Mobile theme name is specified in portal_properties -> mobile_properties.

For the sake of simplicity, CSS files are hardcoded in the mobile main template gomobile/mobile/skins/mobile_base/main_template.pt
and Plone's CSS registry is ignored for mobile.

Mobile aware and convergence aware base viewlets are available in gomobile.convergence.browser and gomobile.mobile.browser packakges.

Viewlet configuration
+++++++++++++++++++++

Mobile theme layer has its own viewlet configuration.

To rearrange mobile theme viewlets, go http://mobi.localhost/@@manage-viewlets

Image resizing
==============

Images can be automatically resized to fit for mobile screen. The following options are availble

* Scale by maximum screen width (good for logos)

* Scale by maximum screen height

* Manually enforce dimensions

Please see gomobile.mobile.browser.resizer for more information about this functionality.

User agent sniffing
-------------------

To achieve the maximum usability mobile pages must be tailored for each handset individually. This means

* Resizing images suitable for the handset small or big screen resolution

* Serving correct video files depending on the handset support (RTSP, 3G, iPhone MP4 progressive download and such)

* Change link and button sizes depending whether the handset is touchscreen based or keypad based

* Disable site features depending on whether the handset supports them (downloadable map locations, ringtones, wallpapers)

* Use location based information when available 

State of the art `mobile.sniffer <http://code.google.com/p/mobilesniffer/>`_ library is used in this project.
It is an generic middleware supporting several different handset databases. To make the sniffing more accurate, 
sniffing can source information from multiple databases once.

Traffic analyzing
-----------------

Mobile sites cannot use Javascript based traffic analysing (Google Analytics).

gomobile.analytics provides SQL based visitor logging

* Unique visitors

* Visitor revisits

* Pages/visiting session

[TODO: Need to publish code for this]

Performance
-----------

archetypes.schemaextender has performance issues.

If this is an issue please install archetypes.schematuning package.

Unit tests
----------

Unit tests are available for all packages.

Roadmap
-------

* Launch GoMobile community in GetPaid fashion

* Recruit sponsors/clients

* Build the best mobile content management system in the world

History
-------

This project started as an internal Twinapex effort and was test-driven
on few sites before becoming public. To embrace the open source 
and make this product a great success we decided to spin off it.

Authors
-------

The project is hosted at `Google Code project repository <http://code.google.com/p/plonegomobile>`_.

Currently project is maintained by`Twinapex Research <http://www.twinapex.com>`_ team and friends. Email: mikko.ohtamaa@twinapex.com.

Twinapex Research - high quality Python and mobile hackers for hire. We have 50+ years of mobile site expertise and 10+ years of Plone expertise.

