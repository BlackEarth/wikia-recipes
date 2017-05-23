
import json, os, re, requests, traceback
from lxml.etree import Entity
from bl.url import URL
from bxml import XML
from bxml.builder import Builder
from bf.image import Image

NUM_RECIPES = 1000
MIN_PPI = 100
MIN_IMAGE_WIDTH = 1000
MIN_IMAGE_HEIGHT = None

NS = {
    'aid':"http://ns.adobe.com/AdobeInDesign/4.0/",
    'aid5':"http://ns.adobe.com/AdobeInDesign/5.0/",
}
E = Builder(**NS)._

CATEGORIES = [
    ('Beverage_Recipes', 'Beverages')
    ('Appetizer_Recipes', 'Appetizers')
    ('Main_Dish_Recipes', 'Main Dishes')
    ('Side_Dish_Recipes', 'Side Dishes')
    ('Dessert_Recipes', 'Desserts')
]

PATH = os.path.dirname(os.path.abspath(__file__))
WIKI_URL = "http://recipes.wikia.com"
ARTICLES_URL = WIKI_URL+ "/api/v1/Articles"
CONTENT_PATH = os.path.join(os.path.dirname(PATH), 'data')
IMAGE_PATH = os.path.join(CONTENT_PATH, 'images')
PSTYLEKEY = "{%(aid)s}pstyle" % NS

def main():
    category_counts = {}
    for category_label, category_title in CATEGORIES:
        print('\n== %s ==' % category_label)
        xml = XML()
        xml.fn = os.path.join(CONTENT_PATH, '%s.xml' % category_label)
        items_elem = E.items()
        xml.root = E.category(
            E.title(category_title, Entity('#xA'), {PSTYLEKEY:'category-title'}), 
            items_elem)
        list_url = ARTICLES_URL + "/List?category=%s&limit=%d" % (category_label, NUM_RECIPES)
        recipe_list = requests.get(list_url).json()
        items = recipe_list.get('items')
        print(len(items), 'items')
        for item in items:
            try:
                print(items.index(item), '\t', item.get('id'), '\t', item.get('title'))
                item_elem = get_item_elem(item)
                if item_elem is not None:
                    items_elem.append(item_elem)
            except:
                print(traceback.format_exc())
        xml.write(pretty_print=True, canonicalized=False)
        category_counts[category_label] = len(xml.root.xpath("//item"))
    print(json.dumps(category_counts, indent=2))

def get_item_elem(item, only_with_images=True):
    attrib = {k:str(item[k]) for k in item.keys()}
    elem = E.item(**attrib)

    details_url = ARTICLES_URL + '/Details?ids=%(id)s' % attrib
    # print(details_url)
    item_details = requests.get(details_url).json()['items'][attrib['id']]
    if item_details.get('type')=='category' \
    or 'User_blog:' in item_details.get('url'):    # don't include categories or user blog entries
        return
    keys = item_details.keys()
    for key in list(set(['id', 'title', 'type', 'ns']) & set(keys)):
        elem.set(key, str(item_details[key]))
    
    img_elem = None

    if 'thumbnail' in keys and item_details['thumbnail'] is not None \
    and 'original_dimensions' in keys and item_details.get('original_dimensions') is not None :
        
        dimensions = item_details['original_dimensions']


        if (MIN_IMAGE_HEIGHT is None 
            or (type(dimensions.get('height'))==int and dimensions['height'] >= MIN_IMAGE_HEIGHT)) \
        and (MIN_IMAGE_WIDTH is None 
            or (type(dimensions.get('width'))==int and dimensions['width'] >= MIN_IMAGE_WIDTH)): 
        
            img_elem = get_img_elem(item_details['thumbnail'], MIN_IMAGE_WIDTH)
            if img_elem is not None:
                elem.append(img_elem)

        elif (type(dimensions.get('width'))==int and dimensions['width'] >= MIN_IMAGE_WIDTH / 2):

            img_elem = get_img_elem(item_details['thumbnail'], MIN_IMAGE_WIDTH)
            if img_elem is not None:
                img_elem.tag = 'thumb_img'
                elem.append(img_elem)

    if img_elem is not None or only_with_images != True:
        content_url = ARTICLES_URL + '/AsSimpleJson?id=%(id)s' % attrib
        item_content = requests.get(content_url).json()

        for section in item_content.get('sections'):
            elem.append(get_section_elem(section, details=item_details))

        url = url = WIKI_URL + item_details.get('url')
        elem.append(
            E.section(
                E.paragraph({PSTYLEKEY:"source"}, "Source: ", 
                    E.a(url.replace('http://',''), Entity("#xA"), title=url))))

        return elem

def get_section_elem(item, details=None):
    elem = E.section(level=str(item.get('level')))
    if item.get('title') is not None:
        e = E("h%d" % item.get('level'), item.get('title'), Entity('#xA'))
        e.set(PSTYLEKEY, 'h%s' % elem.get('level'))
        elem.append(e)

    for content in item.get('content'):
        elem.append(get_content_elem(content, elem))

    return elem

def get_img_elem(full_url, display_width):
    md = re.search(r"(^.*\.(?:jpe?g|gif|png|tiff?|pdf))", full_url, flags=re.I)
    if md is not None:
        url = md.group()
        basename = re.sub("%..", "+", os.path.basename(url))
        imgfn = os.path.join(IMAGE_PATH, basename)
        i = Image(fn=imgfn)
        if not(os.path.exists(imgfn)):
            result = requests.get(md.group())
            i.data = result.content
            i.write()
        w, h, x, y = i.identify(format="%w,%h,%x,%y").split(',')
        print(w, h, x, y, os.path.basename(i.fn))
        density = int(MIN_PPI * int(w)/display_width)
        i.mogrify(format="jpg", density="%dx%d" % (density, density))
        i.fn = os.path.splitext(i.fn)[0]+'.jpg'
        # i.mogrify(crop="%dx%d" % (int(w), int(int(w)*.67)), gravity="Center")
        w, h, x, y = i.identify(format="%w,%h,%x,%y").split(',')
        print(w, h, x, y, os.path.basename(i.fn))
        img = E.img({'href':"file://"+os.path.relpath(i.fn, CONTENT_PATH)})
        return img

def get_content_elem(item, parent_elem):
    elem = E(item.get('type'), item.get('text') or '')
    if elem.text not in [None, '']: 
        elem.append(Entity("#xA"))
    elem.set(PSTYLEKEY, item.get('type'))
    for element in item.get('elements') or []:
        elem.append(get_element(element))
    return elem

def get_element(item):
    elem = E.element(item.get('text') or '', *[get_element(i) for i in item.get('elements') or []], Entity('#xA'))
    return elem

if __name__=='__main__':
    main()
