# -*- coding: utf-8 -*-
import re, os
from subprocess import Popen, PIPE
import argparse
from rapydml.markuploader import load
from rapydml.compiler import Parser, __file__ as rapydml_compiler_path
import json

RAPYDML_DIR = os.path.abspath(os.path.dirname(rapydml_compiler_path))

# read config

def read_config():
    self_path =  os.path.abspath(os.path.dirname(__file__))
    ml_cmp_conf =  os.path.join(self_path,'ml_cmp.conf')
    if os.path.isfile(ml_cmp_conf):
        with open(ml_cmp_conf, 'r') as f:
            cfg = f.read()
        try:
            cfg = json.loads(cfg)
        except ValueError:
            raise ValueError('Invalid ml_cmp.conf: %s' % ml_cmp_conf)
        # check settings
        missing = set(('node', 'rapydscript', 'rs_options')) - set(cfg.keys())
        if missing:
            raise ValueError('Missing settings in ml_cmp.conf: %s' % missing)

        ret = [
                [   os.path.normpath(cfg['node']),
                    os.path.normpath(cfg['rapydscript'])
                ],
                cfg['rs_options']
        ]
        return ret

RS_CMD, RS_OPT = read_config()


class ShellError(Exception):
	"""
	Helper class for standardizing error messages
	"""

	def __init__(self, message):
		self.message = message

	def __str__(self):
		return self.message

def buff_split(s):
    """
    split in 3 parts
    - html_tst
    - templates
    - RS script
    """
    _re = re.compile('^#-{3,} *< *(?:TEMPLATES|RS_SCRIPT) *> *-{3,}', flags = re.MULTILINE)
    return _re.split(s)

def get_parser(ml_first_line):
    markup = ml_first_line.strip()
    if  markup.startswith('#!markup'):
        markup = markup.split('=')[1:]
        markup = markup and markup[0].strip() or ''
        available_markup = os.listdir(os.path.join(RAPYDML_DIR, 'markup'))
        if not (markup and markup in available_markup):
            raise RuntimeError('Invalid markup: %s' % markup)
    else:
        markup = 'html'
    markup_lang = load(markup, RAPYDML_DIR)
    ret = Parser(markup_lang)
    ret.set_rapydscript(RS_CMD, RS_OPT)
    return ret

def write_html_tst(ml_s, html_fname):
    """
    ml_s - RapydML string
    """
    if not ml_s:  return

    ml_lines = ml_s.splitlines(True)
    html = get_parser(ml_lines[0])
    with open(html_fname, 'w') as output:
        output.write(html._parse(ml_lines))

def ml_templ_to_html(ml_s):
    """
    ml_s - RapydML string
    """
    if not ml_s:  return ''

    ml_lines = ml_s.splitlines(True)
    html = get_parser(ml_lines[0])
    return html._parse(ml_lines)

def split_templates_css(ml_s):
    ml_s = re.sub('^ *\n', '', ml_s, flags = re.MULTILINE)
    _re = re.compile(
            "^(script *\( *type *= *(?:\"|')text */ *(?!javascript)(?:\"|') *, *id *= *(?:\"|')(?P<id>[0-9a-z_\-.]+)(?:\"|') *\) *:)|" + \
        "(?:css *\( *(store_in *= *(?:\"|')(?P<store_in>[0-9a-z_\-.]+)(?:\"|'))? *\) *:)" ,
                        flags = re.MULTILINE | re.IGNORECASE)
    templs = _re.split(ml_s)
    ret = {}
    i = 0
    if templs[0]=='':
        templs.pop(0)
    while i <len(templs):
        templ_html = re.sub('^(    )|( *\r\n\|\n)', '', templs[i+1], flags = re.MULTILINE) # remove indent and empty lines
        #templ_html = re.sub('^ *\n', '', templ_html, flags = re.MULTILINE) # remove indent
        css, templ_html =  split_css( templ_html)
        ret[templs[i]] = dict(templ ='', css='')
        ret[templs[i]]['css'] = css
        ret[templs[i]]['templ'] =  ml_templ_to_html(templ_html)
        i+=2
    return ret

def split_css(ml_templ):
    """
    return  [css, ml_template]
    """
    re_css = re.compile( r'^( *)css *\( *\) *: *((?:\n\1 +.+)*\n?)', flags=re.MULTILINE | re.IGNORECASE)
    lst = re_css.split(ml_templ)
    if  len(lst) < 4:
        ret = ['', ml_templ]
    else:
        pref = lst[0]
        # lst[1] == '   ' - indent spaces
        css_def = lst[2] # css content
        rest = lst[3] # templ content
        if not re.sub('\n|\r| ','',css_def):
            css_def = ''
        ret = [css_def, pref + rest]
    return ret

def insert_templ_css_tab(rs_s, templs):
    def templ_replacer(m):
        id = m.group(2)
        indent = ' '*(len(m.group(1)) + 4)
        s = m.group(1) + '"""<!-- %s -->%s%s"""' % ( id,'\n'+indent, re.sub('\r\n|\n', '\n'+indent, templs[id]['templ']))
        return s
    ret  = re.sub('(^ *(?![#\s]).+)@TMPL\( *([a-z0-9_\-.]+) *\)', templ_replacer, rs_s,  flags = re.MULTILINE )

    def css_replacer(m):
        id = m.group(2)
        indent = ' '*(len(m.group(1)) + 4)

        css = templs[id]['css']
        if not css:
            s = m.group(1) +  ('None #%s.css\n' % id)
        else:
            s = m.group(1) + \
                '"""/* %s.css */ %s"""' % ( id, re.sub('\r\n|\n', '\n'+indent, css))
        return s
    ret  = re.sub('^(.+)@CSS\( *(\w+) *\)', css_replacer, ret,  flags = re.MULTILINE )

    return ret


def make_pyj_js(rs_s, dest_base_fname):
    """
    produce 2 files
        - dest_base_fname.pyj
        - dest_base_fname.js
    rs_s - RapydScript string
    dest_base_fname - 'd:/dfsdf/sdfsdf/out_name' - no ext!
    """
    from os  import path

    pyj_fname =  path.normpath( dest_base_fname+'.pyj')
    js_fname = path.normpath(dest_base_fname+'.js')

    with open(pyj_fname, 'w') as file_pyj:
    	file_pyj.write(rs_s)

    #cmd = RapydRS_cmd
    cmd_lst = RS_CMD + [pyj_fname] + RS_OPT + ['-o', js_fname]
    #compile pyj to js
    result = Popen(cmd_lst,
                    stdout = PIPE, stderr = PIPE, shell = True).communicate()
    if result[1]:
    	raise ShellError("'%s' triggered the following OS error: %s" %
                               ('make_pyj_js', result[1]))


def remove_empty_lines(s):
    #s.decode('utf-8')
    s1 = re.sub('^\s*$\s', '', s, flags=re.MULTILINE)
    return s1


def split_script_css(raw_script_css):
    script_css = re.sub('^\s*$', '', raw_script_css, flags = re.MULTILINE)
    _re = re.compile(   "^(((?:script)|(?:css)).*:\s*$(?:(?:\n +.*\s*$)*))" ,
                        flags = re.MULTILINE | re.IGNORECASE)

    script_css_lst = _re.findall(script_css)
    #script_css_lst = [ ('css(...) ...'     ,   'css'),
    #                   ('script(...) ...'  ,   'script'),
    #  ....                            ]
    script = {}
    css = {}
    for el, el_type in script_css_lst:
        el_head , el_body = el.split('\n', 1)
        if el_type.lower()  == 'css':
            store_in = re.findall('store_in *= *(?:\'|")([a-z0-9_\-./]+)(?:\'|")',
                                    el_head)[0]
            css[store_in] = el_body
        elif el_type.lower()  == 'script':
            id = re.findall('id *= *(?:\'|")([a-z0-9_\-.]+)(?:\'|")',
                                    el_head)[0]
            script[id] = dict(templ ='', css='')
            templ_css, templ_html =  split_css( el_body)
            script[id]['css'] = templ_css
            script[id]['templ'] = unicode(ml_templ_to_html(templ_html), 'utf-8')
    return dict(script = script, css= css)


def store_css(css_frags, section_name, base_path):
    def _store_css(css_fname, section_name, css_frag):
        css_body = ''
        if os.path.exists(css_fname):
            with open(css_fname, 'r') as f:
            	 css_body =  f.read()

        rslt = re.split('(^ */\* *-+ *< *%s *> *-+ *\*/ *\n)' %  section_name ,
                        css_body, flags = re.MULTILINE | re.IGNORECASE)
        if len(rslt)>1:
            tmp = re.split(r'(^ */\* *-+ *< *[a-z0-9_\-./\\]+ *> *-+ *\*/ *$)', rslt[2],
                            1,  flags = re.MULTILINE | re.IGNORECASE)
            ret = rslt[0] + rslt[1] + ''.join([css_frag, '\n'] + tmp[1:])
        else:
            ret =  css_body + \
                        ('\n/*-----------< %s >-----------*/\n' %  section_name) + \
                        css_frag
        with open(css_fname, 'w') as f:
        	 f.write(ret)
        return ret

    NP = os.path.normpath
    for css_fname in css_frags:
        if not re.match( r'([a-z0-9_\-]+(/|\\|\.(?!\.))?)+\.css', css_fname):
            raise RuntimeError('bad css filename^ %s' % css_fname)
        abs_css_fname = NP(os.path.join(base_path, css_fname))
        _store_css(abs_css_fname, section_name, css_frags[css_fname])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type = str, help = 'file.ml_cmp')
    parser.add_argument('-od','--outdir', type = str,
                    default = '',
                    help = 'output dir: abs - "d:/dir" or  relative - "bar/foo"')
    args = parser.parse_args()
    NP = os.path.normpath
    cmp_absbase_fname, ext = os.path.splitext(os.path.abspath(args.src))
    cmp_path, cmp_base_fname = os.path.split(cmp_absbase_fname)
    out_path = NP(os.path.join(cmp_path, args.outdir ))
    html_test_fname =  NP(os.path.join(out_path, cmp_base_fname +'_test.html' ))
    pyj_js_base_fname = NP(os.path.join(out_path, cmp_base_fname))

    with open(cmp_absbase_fname + ext, 'r') as f:
    	 ml_cmp =  remove_empty_lines(f.read())
    ml_test, raw_templates, rs_script =  buff_split(ml_cmp)
    #   templates = split_templates_css(raw_templates)
    script_css = split_script_css(raw_templates)
    # replace @TEMPL() and @CSS() in rs_script
    rs_script = insert_templ_css_tab(rs_script, script_css['script'])
    # write & compile scripts  - .pyj, .js
    make_pyj_js(rs_script, pyj_js_base_fname)
    print 'Writing pyj/js files:'
    print '\t', pyj_js_base_fname + '.pyj'
    print '\t', pyj_js_base_fname + '.js'
    write_html_tst(ml_test, html_test_fname)
    print 'Writing html file:\n\t', html_test_fname
    store_css(script_css['css'], cmp_base_fname, cmp_path)
    if script_css['css']:
        print 'Writing css files:'
        for f in script_css['css'].keys():
            print '\t', f
    print 'Done!'

if __name__ == '__main__':
    main()

