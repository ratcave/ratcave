
Introduction
============

ratCAVE was created to be an API for doing behavioral experiments with animals in a freely-moving virtual reality environment.  While there are many game engines on the market that could support this application, they tended to be very elaborate pieces of software that were really meant for the video game market, and features like *high-temporal performance* (our goal was <3 msecs movement-to-photon lag), *Cubemapping Support* (most game engines required users to dig in pretty deep into a large API toreach this level), and *ease of use* (most game engines were written in low-level programming languages and steep learning curves) weren't easily reachable, and *open-source*.  Pyglet and Psychopy, on the other hand, had these features in the bag, but they didn't explicitly support 3D graphics, so the approach we decided on in the end was to build on that platform.  

What we've found is that ratCAVE makes for a succinct 3D graphics engine, even for simple tasks, and so development effort is put into overall performance for projects even beyond the VR projects in our lab.

While Python is not typically the language thought of when looking for high-performance graphics, the maturity of modern OpenGL means that very little of the graphics rendering needs to be done in Python at all.  While we are still at an early stage of development with ratCAVE, we've already reached the requirements listed above, with a goal of continually refactoring and adding features to make ratCAVE the mature backend it has the potential to be.  If you are interested in aiding the development of ratCAVE, either through contributions on GitHub, bug reporting, or even simply testing it out yourself and giving us feedback, we hope you'll get involved and help us develop this little project into something wonderful!

