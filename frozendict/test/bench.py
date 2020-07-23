#!/usr/bin/env python3

def main():
    import timeit
    import uuid
    from string import Template
    from statistics import stdev
    import msutils
    import sys
    
    def autorange(stmt, setup="pass", repeat=5, globals=None, max_retries=100):
        if setup == None:
            setup = "pass"
        
        t = timeit.Timer(stmt=stmt, setup=setup, globals=globals)
        a = t.autorange()
        number = int(a[0] / 5)
        
        if number < 1:
            number = 1
        
        data_min = []
        data = [a[1]]
        
        for x in range(max_retries):
            data.extend(t.repeat(number=number, repeat=repeat))
            sigma = stdev(data) / number
            min_data = min(data)
            result = min_data / number
            result_magnitude = msutils.magnitudeOrder(result)
            
            if 5 * 10**result_magnitude > sigma * 100:
                return (result, sigma)
            
            data_min.append(min_data)
            data = data_min.copy()
        
        raise RuntimeError("Sigma too high!")
    
    
    def getUuid():
        return str(uuid.uuid4())
    
    
    dictionary_sizes = (8, 1000)
    
    print_tpl = "Name: {name: <25} Size: {size: >4}; Keys: {keys: >3}; Type: {type: >10}; Time: {time:.2e}; Sigma: {sigma:.0e}"
    str_key = '12323f29-c31f-478c-9b15-e7acc5354df9'

    benchmarks = (
        {"name": "o.get(key)", "code": "get(key)", "setup": "key = getUuid(); get = o.get", }, 
        {"name": "o[key]", "code": "o[one_key]","setup": "pass", }, 
        {"name": "key in o", "code": "key in o", "setup": "key = getUuid()", },  
        {"name": "key not in o", "code": "key not in o", "setup": "key = getUuid()", },
        {"name": "pickle.dumps(o)", "code": "dumps(o, protocol=-1)", "setup": "from pickle import dumps", },  
        {"name": "pickle.loads(dump)", "code": "loads(dump, buffers=buffers)", "setup": "from pickle import loads, dumps; buffers = []; dump = dumps(o, protocol=-1, buffer_callback=buffers.append)", },  
        {"name": "hash(o)", "code": "hash(o)", "setup": "pass", },   
        {"name": "len(o)", "code": "len(o)", "setup": "pass", },  
        {"name": "o.keys()", "code": "keys()", "setup": "keys = o.keys", },  
        {"name": "o.values()", "code": "values()", "setup": "values = o.values", },  
        {"name": "o.items()", "code": "items()", "setup": "items = o.items", },   
        {"name": "iter(o)", "code": "iter(o)", "setup": "pass", }, 
        {"name": "for x in o", "code": "for _ in o: pass", "setup": "pass", },
        {"name": "for x in o.keys()", "code": "for _ in keys: pass", "setup": "keys = o.keys()", },  
        {"name": "for x in o.values()", "code": "for _ in values: pass", "setup": "values = o.values()", },  
        {"name": "for x in o.items()", "code": "for _ in items: pass", "setup": "items = o.items()", },   
        {"name": "for x in iter(o)", "code": "for _ in iter(o): pass", "setup": "pass", }, 
        {"name": "constructor(d)", "code": "klass(d)", "setup": "klass = type(o)", },
        {"name": "constructor(d.items())", "code": "klass(v)", "setup": "klass = type(o); v = tuple(d.items())", },  
        {"name": "constructor(**d)", "code": "klass(**d)", "setup": "klass = type(o)", },
        {"name": "constructor(o)", "code": "klass(o)", "setup": "klass = type(o)", },
        {"name": "o.copy()", "code": "o.copy()", "setup": "pass", },
        {"name": "o == d", "code": "o == d", "setup": "pass", },
        {"name": "o == o", "code": "o == o", "setup": "pass", },
        {"name": "class.fromkeys()", "code": "fromkeys(keys)", "setup": "fromkeys = type(o).fromkeys; keys = o.keys()", },
        {"name": "repr(o)", "code": "repr(o)", "setup": "pass", },
        {"name": "str(o)", "code": "str(o)", "setup": "pass", },
    )
    
    dict_collection = []
    
    for n in dictionary_sizes:
        d1 = dict()
        d2 = dict()

        for i in range(n-1):
            val = getUuid()
            d1[getUuid()] = val
            d2[i] = val
        
        d1[str_key] = getUuid()
        d2[999] = 999

        fd1 = frozendict(d1)
        fd2 = frozendict(d2)
        
        dict_collection.append({"str": ((d1, fd1), str_key), "int": ((d2, fd2), 6)})
        
    for benchmark in benchmarks:
        print("################################################################################")
        
        for dict_collection_entry in dict_collection:
            for (dict_keys, (dicts, one_key)) in dict_collection_entry.items():
                print("////////////////////////////////////////////////////////////////////////////////")
                
                for o in dicts:
                    if benchmark["name"] == "hash(o)" and type(o) == dict:
                        continue
                    
                    if benchmark["name"] == "constructor(**d)" and dict_keys == "int":
                        continue
                    
                    d = dicts[0]
                    
                    try:
                        bench_res = autorange(
                            stmt = benchmark["code"], 
                            setup = benchmark["setup"], 
                            globals = {"o": o, "getUuid": getUuid, "d": d, "one_key": one_key},
                        )
                    except RuntimeError:
                        name = benchmark["name"]
                        msg = f"Sigma too high for benchmark `{name}`"
                        print(msg, file=sys.stderr)
                        sys.exit(1)

                    print(print_tpl.format(
                        name = "`{}`;".format(benchmark["name"]), 
                        keys = dict_keys, 
                        size = len(d), 
                        type = type(o).__name__, 
                        time = bench_res[0],
                        sigma = bench_res[1],  
                    ))

if __name__ == "__main__":
    main()
