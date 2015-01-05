renrenCawler
============

A cawler based on ghost.py which is used for extract blog in renren web site( the Chinese facebook)

The files ghost.py and logger.py are two files modified based on ghost-01b6 version, they should be copied to the path /$PYTHON_PATH/Lib/site-packages/Ghost.py-0.1b6-py3.4.egg/ghost

The file ghost_renren.py is the main program for the cawler. Here are the steps how to use it

1) After run python ghost_renren.py, the program will ask you about the username and password

2) After type them, there may be the asking about typing the check code if it needed, you can see a web window poped for you to check it.

3) If anything is going well, you can see the log in stdout such as '[x]Getting the blog xxxxxx'

4) After all the blogs have been done, there will be a file called renren_blog.html generated in your path

5) And then the program continues getting images of your account, after it's completed, you can see all the images in the dir 'renren_img'
