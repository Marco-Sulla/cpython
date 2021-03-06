#!/usr/bin/env python3

def main(number):
    import timeit
    import uuid
    import immutables
    from math import sqrt
    from time import time
    
    def mindev(data, xbar = None):
        if not data:
            raise ValueError("No data")
        
        if xbar == None:
            xbar = min(data)
        
        sigma2 = 0
        
        for x in data:
            sigma2 += (x - xbar) ** 2
        
        N = len(data) - 1
        
        if N < 1:
            N = 1
        
        return sqrt(sigma2 / N)
    
    def autorange(stmt, setup="pass", globals=None, ratio=1000, bench_time=10, number=None, max_data=100000):
        if setup == None:
            setup = "pass"
        
        t = timeit.Timer(stmt=stmt, setup=setup, globals=globals)
        break_immediately = False
        
        if number == None:
            a = t.autorange()
            
            num = a[0]
            number = int(num / ratio)
            
            if number < 1:
                number = 1
            
            repeat = int(num / number)
            
            if repeat < 1:
                repeat = 1
        
        else:
            repeat = 1
            break_immediately = True
        
        results = []
        
        data_tmp = t.repeat(number=number, repeat=repeat)
        min_value = min(data_tmp)
        data_min = [min_value]
        
        bench_start = time()
        
        while 1:
            data_min.extend(t.repeat(number=number, repeat=repeat))
            
            if break_immediately or time() - bench_start > bench_time:
                break
        
            data_min.sort()
            xbar = data_min[0]
            i = 0
            
            while i < len(data_min):
                i = len(data_min)
                sigma = mindev(data_min, xbar=xbar)
                
                for i in range(2, len(data_min)):
                    if data_min[i] - xbar > 3 * sigma:
                        break
                
                k = i
                
                if i < 5:
                    k = 5

                if i > max_data:
                    i = max_data
                
                del data_min[k:]
        
        xbar = min(data_min)

        return (xbar / number, mindev(data_min, xbar=xbar) / number)
    
    
    def getUuid():
        return str(uuid.uuid4())
    
    
    dictionary_sizes = (8, 42, 1000)
    
    print_tpl = "Name: {name: <25} Size: {size: >4}; Keys: {keys: >3}; Type: {type: >10}; Time: {time:.2e}; Sigma: {sigma:.0e}"
    str_key = '12323f29-c31f-478c-9b15-e7acc5354df9'

    benchmarks = (
        {"name": "o.set(key, value)", "code": "o.set(key, value)", "setup": "key = getUuid(); value = getUuid()", }, 
    )
    
    dict_collection = []
    
    for n in dictionary_sizes:
        d1 = {}
        d2 = {}

        for i in range(n-1):
            d1[getUuid()] = getUuid()
            d2[i] = i
        
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
                        number = number,
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
    import sys

    number = None
    argv = sys.argv
    len_argv = len(argv)
    max_positional_args = 1
    max_len_argv = max_positional_args + 1
    
    if len_argv > max_len_argv:
        raise ValueError(
            ("{name} must not accept more than {nargs} positional " + 
            "command-line parameters").format(name=__name__, nargs=max_positional_args)
        )
    
    number_arg_pos = 1
    
    if len_argv == number_arg_pos + 1:
        number = int(argv[number_arg_pos])
    
    main(number)
