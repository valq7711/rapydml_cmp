
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
1. Append to the end of `RapydML/rapydml/markup/html` this line: `<*>+ *` - *it is rough solution that allows to use invalid 
html-tags like in `v_hello( :items = 'items'):` in `RapydML` templates. The strict way looks like  `<v_hello>+ *` - see [RapydML](https://github.com/atsepkov/RapydML) for more info.*
 

Compilation
------------
Just run 
```python /path/to/rapydml_cmp.py <cmp_file>```
it should produce 3 files (in the <cmp_file> directory):
   *  <cmp_file>_test.html
   *  <cmp_file>.pyj
   *  <cmp_file>.js


Getting Started
---------------
Here is an example of a simple Vue component RapydScript/RapydML source code [v_hello](https://github.com/valq7711/rapydml_cmp/blob/master/examples/v_hello)
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

    #--------------- demo bootstrap rapydscript block -------------------
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
    
def main():
    # we need to assign our component function to some global object, since RapydScript wraps all code in a function
    if not window.my_vcs:
        window.my_vcs = {}
    window.my_vcs.v_hello = v_hello
    # or it may be just 
    # Vue.component('v_hello', v_hello())  # it will be Vue-global component
if __name__=='__main__':
    main()    
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
  * finally `v_hello.pyj` will be compiled to `v_hello.js` by RapydScript

Known issues
------------
### RapydML

   * **Indentation is very strict**

The indent increment should be the same almost everywhere, so this doesn't work:
```
html:
   head:
            body:    # wrong indent!
```
You can relax inside non-html blocks (like rapydscript or javascript), but don't cross the indentation boundary
   * **Multi-Line tag definition should be glued by `\` despite it is inside parentheses.** The following is allowed: 
```python
...
   div( id= ...,  \
@click  = ...):  # will be glued, so the indent doesn't matter
```
   * `$` **has special meaning**
   
RapydML accepts `$` as token of variable (see RapydML doc), use `\` to escape it. 
```python
   div( @click = 'on_click( \$event, some)'):  # $event - Vue variable, not RapydML, so it should be escaped
   RS:
      def():
         $a = 12  # don't worry - it's inside code block 
```

  *to be continued ...*
