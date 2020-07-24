#!/usr/bin/env python3

def main():
    import timeit
    import uuid
    from statistics import stdev, mean
    import msutils
    import sys
    import immutables
    import copy
    
    def autorange(stmt, setup="pass", repeat=20, globals=None, max_retries=100):
        if setup == None:
            setup = "pass"
        
        if repeat < 2:
            raise ValueError("`repeat` parameter must be >= 2")
        
        t = timeit.Timer(stmt=stmt, setup=setup, globals=globals)
        a = t.autorange()
        number = int(a[0] / 5)
        
        if number < 1:
            number = 1
        
        results = []
        data_min = []
        
        for x in range(max_retries):
            data_tmp = t.repeat(number=number, repeat=repeat)
            data = data_tmp + data_min
            data.sort()
            data = data[:int(len(data) / 2)]
            sigma = stdev(data) / number
            value = mean(data) / number
            value_magnitude = msutils.magnitudeOrder(value)
            
            results.append((value, sigma))
            
            if 3 * 10**value_magnitude > sigma * 100:
                break
            
            data_min.append(min(data_tmp))
        
        sigmas = [x[1] for x in results]
        values = [x[0] for x in results]
        sigma = min(sigmas)
        i = sigmas.index(sigma)
        value = values[i]
        
        return (value, sigma)
    
    
    def getUuid():
        return str(uuid.uuid4())
    
    
    dictionary_sizes = (8, 1000)
    
    print_tpl = "Name: {name: <25} Size: {size: >4}; Keys: {keys: >3}; Type: {type: >10}; Time: {time:.2e}; Sigma: {sigma:.0e}"
    str_key = '12323f29-c31f-478c-9b15-e7acc5354df9'

    benchmarks = (
        {"name": "o.set(key, value)", "code": "o.set(key, value)", "setup": "key = getUuid(); value = getUuid()", }, 
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
        
        imap1 = immutables.Map(d1)
        imap2 = immutables.Map(d2)
        
        dict_collection.append({"str": ((fd1, imap1), str_key), "int": ((fd2, imap2), 6)})
        
    for benchmark in benchmarks:
        print("################################################################################")
        
        for dict_collection_entry in dict_collection:
            for (dict_keys, (dicts, one_key)) in dict_collection_entry.items():
                print("////////////////////////////////////////////////////////////////////////////////")
                
                for o in dicts:
                    bench_res = autorange(
                        stmt = benchmark["code"], 
                        setup = benchmark["setup"], 
                        globals = {"o": o, "getUuid": getUuid, "one_key": one_key},
                    )

                    print(print_tpl.format(
                        name = "`{}`;".format(benchmark["name"]), 
                        keys = dict_keys, 
                        size = len(o), 
                        type = type(o).__name__, 
                        time = bench_res[0],
                        sigma = bench_res[1],  
                    ))

if __name__ == "__main__":
    main()
