import re
import time
import os

from ghost import Ghost

def saveImage(imgbytes, imgpath):
    wfile = open(imgpath, "wb")
    for i in range(0, imgbytes.size()):
        wfile.write(imgbytes[i])
    wfile.close()
    
def getImage(ghost):
    html = ghost.content
    reg = r'id="album-box-(\d+?)"'
    albumidre = re.compile(reg)
    albumidlist = re.findall(albumidre,html)
    albumlnklist = []

    #first check the img path if not exist just create one
    imgdir = 'renren_img'
    if not os.path.exists(imgdir) :
        os.makedirs(imgdir)
        
    #save the albumlnk first to avoid the problem of changing ghost
    for albumid in albumidlist:
        # Get the image album link
        albumlnk = ghost.get_attribute('a[id="album-%s"]' % albumid, 'href')
        albumlnklist.append(albumlnk)

    #start to get the image from different albums
    for albumlnk in albumlnklist:
        page,resource = ghost.open(albumlnk)
        ghost.wait_for_selector('a[class="p-b-item"]')
        html = ghost.content

        # Find the img link
        # 'r' means raw string, all the character should be considered as a normal character
        reg = r';(http://.+?/(p_large_|large_|original_|h_large_).+?\.jpg)&quot;'
        imglnkre = re.compile(reg)
        imglnklist = re.findall(imglnkre,html)
        
        print('image list in album lnk %s is %s' % (albumlnk,imglnklist))

        if len(imglnklist) != 0 :
            i = 0
            for imglnk in imglnklist:
                #trim some blank character (\u200b) in some awful link
                imglnk = imglnk[0].replace('\u200b', '')
                
                #create the image name
                #first get the date info
                reg = r'/(\d{8})/'
                datereg = re.compile(reg)
                imgdate = re.search(datereg, imglnk).group(1)
                imgpath = '%s/%s-%d.jpg' % (imgdir,imgdate,i)

                #save the image to the disk
                page, resource = ghost.open(imglnk)
                ghost.wait_for_page_loaded()
                saveImage(page.content, imgpath)
                i = i + 1

                print('Created the img %s' % imgpath)

    print('Get all the image, check the dir %s and just enjoy it' % imgdir)

def getUserId(html):
    reg = r'href="http://www\.renren\.com/(\d{2,}?)/profile"'
    idre = re.compile(reg)
    userid = re.search(idre, html)
    if userid != None :
        return userid.group(1)
    else :
        return None

def getBlog(ghost):
    lastblog = False
    i = 0;
    html = ghost.content
    blogfile = 'renren_blog.html'
    wfile = open(blogfile, "w", encoding='utf-8')

    #find the first blog url
    reg = r'href="(http://blog\.renren\.com/blog/\d{2,}?/.+?\?bfrom=.+?)"'
    blogre = re.compile(reg)
    blogurl = re.search(blogre, html).group(1)
   
    while True:
        #open the blog page
        i = i + 1
        print('[%d]Getting the blog:%s' % (i,blogurl))
        page, resource = ghost.open(blogurl)
        ghost.wait_for_page_loaded()
                
        #handle the blog information
        title = ghost.get_text('h2[class="blogDetail-title"]')
        #print("Title:" + title)
        wfile.write("<h1>" + title + "</h1>\n")
        content = ghost.get_text('div[id="blogContent"]')
        #print("Content:" + content)
        wfile.write("<p>" + content + "</p>\n")
        
        #checking whether it's the last one
        lastblog = not ghost.exists('div[class="blogDetail-pre"]')
        
        if lastblog:
            #Jump out the loop
            break
        else :
            #goto the pre-blog url
            blogurl = ghost.get_attribute('div[class="blogDetail-pre"] > a', 'href')
            
    print("Blog extracting finished, total %d blog, check the file %s and just enjoy it" % (i, blogfile))
    wfile.close()    
            
            
def hasCheckCode(ghost):
    value, resource = ghost.wait_for_text('您输入的验证码不正确', 3)
    return value

ghost = Ghost(wait_timeout=10, display=True)

#here you can set your proxy ip
#ghost.set_proxy('http','109.105.1.52',8080)

# Opens the web page 
page, resource = ghost.open('http://www.renren.com')

username = input('Please input your username:')
password = input('Please input your password:')

ghost.wait_for_page_loaded()
ghost.set_field_value('input[id="email"]', username)
ghost.set_field_value('input[id="password"]', password)
ghost.click('input[id="login"]')
ghost.wait_for_page_loaded()

#here for the checkcode input
if hasCheckCode(ghost) :
    ghost.show()
    checkcode = input('Please input the checkcode:')
    ghost.hide()
    ghost.set_field_value('input[id="icode"]', checkcode)
    ghost.click('input[id="login"]')

#enter my blog web site
ghost.wait_for_text('首页')

#get the use id from the homepage
userid = getUserId(ghost.content)
if userid == None :
    print('[Opps]The id pattern is changed, checking that by the web tools')
    exit()
	
#first get the private blog
page, resource = ghost.open('http://blog.renren.com/blog/%s/myBlogs' % userid)
ghost.wait_for_page_loaded()
getBlog(ghost)

#then get the private image
page, resource = ghost.open('http://photo.renren.com/photo/%s/albumlist/v7?showAll=1#' % userid)
ghost.wait_for_page_loaded()
getImage(ghost)

