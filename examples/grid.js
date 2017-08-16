(function(){
"use strict";
function ՐՏ_in(val, arr) {
    if (typeof arr.indexOf === "function") {
        return arr.indexOf(val) !== -1;
    }
    return arr.hasOwnProperty(val);
}
function ՐՏ_Iterable(iterable) {
    var tmp;
    if (iterable.constructor === [].constructor || iterable.constructor === "".constructor || (tmp = Array.prototype.slice.call(iterable)).length) {
        return tmp || iterable;
    }
    return Object.keys(iterable);
}
function range(start, stop, step) {
    var length, idx, range;
    if (arguments.length <= 1) {
        stop = start || 0;
        start = 0;
    }
    step = arguments[2] || 1;
    length = Math.max(Math.ceil((stop - start) / step), 0);
    idx = 0;
    range = new Array(length);
    while (idx < length) {
        range[idx++] = start;
        start += step;
    }
    return range;
}
function ՐՏ_eq(a, b) {
    var ՐՏitr3, ՐՏidx3;
    var i;
    if (a === b) {
        return true;
    }
    if (Array.isArray(a) && Array.isArray(b) || a instanceof Object && b instanceof Object) {
        if (a.constructor !== b.constructor || a.length !== b.length) {
            return false;
        }
        if (Array.isArray(a)) {
            for (i = 0; i < a.length; i++) {
                if (!ՐՏ_eq(a[i], b[i])) {
                    return false;
                }
            }
        } else {
            if (Object.keys(a).length !== Object.keys(b).length) {
                return false;
            }
            ՐՏitr3 = ՐՏ_Iterable(a);
            for (ՐՏidx3 = 0; ՐՏidx3 < ՐՏitr3.length; ՐՏidx3++) {
                i = ՐՏitr3[ՐՏidx3];
                if (!ՐՏ_eq(a[i], b[i])) {
                    return false;
                }
            }
        }
        return true;
    }
    return false;
}

(function(){

    var __name__ = "__main__";

    var __name__;
    function get_grid_vc() {
        var vc;
        vc = {};
        vc.delimiters = [ "${", "}" ];
        vc.template = '<!-- grid_template -->\n                          <table>\n                              <thead>\n                                  <tr>\n                                      <th v-for="key in columns" @click="sortBy(key)" :class="{ active: sortKey == key }">\n                                          ${ key | capitalize }\n                                          <span class="arrow" :class="sortOrders[key] > 0 ? \'asc\' : \'dsc\'" />\n                                      </th>\n                                  </tr>\n                              </thead>\n                              <tbody>\n                                  <tr v-for="entry in filteredData">\n                                      <td v-for="key in columns">\n                                          ${entry[key]}\n                                      </td>\n                                  </tr>\n                              </tbody>\n                          </table>\n                      ';
        vc.props = {
            data: Array,
            columns: Array,
            filterKey: String
        };
        vc.data = function() {
            var columns, col_name, sortOrders;
            columns = this.columns;
            sortOrders = (function() {
                var ՐՏidx1, ՐՏitr1 = ՐՏ_Iterable(columns), ՐՏres = {}, col_name;
                for (ՐՏidx1 = 0; ՐՏidx1 < ՐՏitr1.length; ՐՏidx1++) {
                    col_name = ՐՏitr1[ՐՏidx1];
                    ՐՏres[col_name] = 1;
                }
                return ՐՏres;
            })();
            return {
                sortKey: "",
                sortOrders: sortOrders
            };
        };
        vc.computed = {};
        vc.computed.filteredData = function() {
            var sortKey, filterKey, order, data, row;
            sortKey = this.sortKey;
            filterKey = this.filterKey && this.filterKey.toLowerCase();
            order = this.sortOrders[sortKey] || 1;
            data = this.data;
            if (filterKey) {
                data = (function() {
                    var ՐՏidx2, ՐՏitr2 = ՐՏ_Iterable(data), ՐՏres = [], row;
                    for (ՐՏidx2 = 0; ՐՏidx2 < ՐՏitr2.length; ՐՏidx2++) {
                        row = ՐՏitr2[ՐՏidx2];
                        if (Object.keys(row).some(function(col) {
                            return ՐՏ_in(filterKey, new String(row[col]).toLowerCase());
                        })) {
                            ՐՏres.push(row);
                        }
                    }
                    return ՐՏres;
                })();
                "\n            f_data = []\n            for row in this.data:\n                for col in row: \n                    if filterKey in String(row[col]).toLowerCase():\n                        f_data.push(row) \n            data =  f_data            \n            ";
            }
            if (sortKey) {
                data = data.slice(0).sort(function(a, b) {
                    a = a[sortKey];
                    b = b[sortKey];
                    if ((a === b || typeof a === "object" && ՐՏ_eq(a, b))) {
                        return 0;
                    }
                    return (a > b && 1 || -1) * order;
                });
            }
            return data;
        };
        vc.filters = {};
        vc.filters.capitalize = function(str) {
            return str[0].toUpperCase() + str.slice(1);
        };
        vc.methods = {};
        vc.methods.sortBy = function(key) {
            this.sortKey = key;
            this.sortOrders[key] = this.sortOrders[key] * -1;
        };
        return vc;
    }
    function main() {
        if (!window.my_vcs) {
            window.my_vcs = {};
        }
        window.my_vcs.grid = get_grid_vc;
    }
    if (__name__ = "__main__") {
        main();
    }
})();
})();
