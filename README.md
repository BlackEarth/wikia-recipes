# wikia-recipes
Python package to create a cookbook from <http://recipes.wikia.com>.

## To Install:
* Make sure you have Python 3 installed and available on your system as the command "python3" (see <http://python.org>). In other words, if you open a command prompt, you should be able to get Python 3 like this:
```bash
    $ python3
    Python 3.5.3 (default, Apr 23 2017, 18:09:27) 
    [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 
```

* You also need to have graphicsmagick (see <http://graphicsmagick.org>) installed and available as the command "gm". I.e.,
```bash
    $ gm
    GraphicsMagick 1.3.25 2016-09-05 Q8 http://www.GraphicsMagick.org/
    Copyright (C) 2002-2016 GraphicsMagick Group.
    Additional copyrights and licenses apply to this software.
    See http://www.GraphicsMagick.org/www/Copyright.html for details.
    Usage: gm command [options ...]

    Where commands include: 
          batch - issue multiple commands in interactive or batch mode
      benchmark - benchmark one of the other commands
        compare - compare two images
      composite - composite images together
        conjure - execute a Magick Scripting Language (MSL) XML script
        convert - convert an image or sequence of images
           help - obtain usage message for named command
       identify - describe an image or image sequence
        mogrify - transform an image or sequence of images
        montage - create a composite image (in a grid) from separate images
           time - time one of the other commands
        version - obtain release version
    $ 
```

* Open a command prompt (if you haven’t already) and type the following commands:
```bash
    $ cd path/to/wikia-recipes
    $ ./install
    $ source venv
```

* Now you can build the recipe XML data:
```bash
    $ python wr/get_recipes_xml.py
```

* And then you can open the recipes template (in interior/Recipes.idml) and start playing with the XML data.
