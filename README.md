
rapydml_cmp
===========
Vue-components generator

Installation
------------
1. Install [RapydScript](https://github.com/atsepkov/RapydScript)
    * **Note**: if there are any problems with RapydScript you can just download & unpack it to anywhere
    
1. Install [RapydML](https://github.com/atsepkov/RapydML)
1. Replace `RapydML/rapydml/compiler.py` with one from this repo
1. Put `rapydml_cmp.py, ml_cmp.conf`  in the root of RapydML
1. Adjust the paths to `node` and `rapydscript` by editig ml_cmp.conf

Getting Started
---------------
Here is an example of a simple Vue component RapydScript/RapydML source code [v_hello](https://github.com/valq7711/rapydml_cmp/examples/v_hello)
```python
RS = code_block( script(type = 'text/javascript'), 'rapydscript')
#---------------------  demo-test.html ---------------   
html:
    head:
        meta(charset='utf-8'):
        script(src='vue.js'):
        script(src='v_hello.js'):
        title:
            "demo-test v_hello.js"
    body:
        div(id = 'container'):
            v_hello( :items = 'items'):

    #--------------- demo bootstrap --------------------
    RS:
        v_opt = {
            el : '#container', 
            data : {
                items : [ {id : 1, value : 'one'}, {id : 2, value : 'two'},  {id : 3, value : 'three'} ]
            },
            components : {'v_hello': my_vcs.v_hello()},
        }
        window.v = new Vue(v_opt)
#-------------------------  < TEMPLATES > ----------------------
script( type = 'text/vuetemplate', id = "v_hello_tmpl" ):
    div():
        h4:
            '${ header_d }'
        div(v-for = 'it in items' , :id =  'it.id'):
            '${ it.value }'
        div():
            'Count = ${items_count}'
            
#----------------------  < RS_SCRIPT > -------------------------
def v_hello():
    vc = {}
    vc.template = @TMPL(v_hello_tmpl)
    vc.delimiters = ['${','}']
    vc.props =  {
            items : Array,
            header : String
    }
    vc.data = def(): return { header_d :  this.header or 'v_hello component'};

    vc.computed = {}
    vc.computed.items_count = def(): return len(this.items);
    return vc    
# To prevent flooding global space RapydScript wraps all code in a function
# so, we need to assign our component function to some global object
if not window.my_vcs:
    window.my_vcs = {}
window.my_vcs.v_hello = v_hello
# or it may be just 
# Vue.component('v_hello', v_hello())  # it will be global component
```
The code consits of three sections:
1. From the begining to `#---< TEMPLATES >---` 
1. Between `#---< TEMPLATES >---` and `#---< RS_SCRIPT >---`
1. From`#---< RS_SCRIPT >---` to the end

The **First** section will be converted to a regular html-file like `v_hello_test.html` by RapydML - thus, we will have demo-test of the component.

The **Second** section will be:
  * splited to templates by `script( type= 'text/vuetemplate', id = 'awesome_id')`
  * converted to a `html-string` or several ones corresponding to splitting result
  * used to replace the pseudocode like `@TMPL(awesome_id)` in the **Last** section.

The **Last** section will be:
  * searched for `@TMPL(awesome_id)` that will be replaced with corresponding `html-string`
  * saved as `v_hello.pyj` - regular rapydscript file with embedded template that could be `imported` in another `file.pyj` or vue-component file like this one!     


