
import json
from colorama import Fore, Style


import base64
import codecs
from functools import partial

import hashlib as md5
from Crypto.Cipher import AES, DES, DES3, Blowfish
from Crypto.Util.Padding import unpad
    
def decode(encoded_text: str, save_result) -> str:
    import zlib, gzip, bz2, lzma, codecs, zipfile, brotli, binascii, quopri

    def uncompressed_zlib(data):
        try:
            return zlib.decompress(data) 
        except:
            return None 

    def uncompressed_gzip(data):
        try:
            return gzip.decompress(data) 
        except:
            return None 
    def uncompressed_gzip2(data):
        try:
            return gzip.decompress(data, 16 + gzip.MAX_WBITS) 
        except:
            return None
    def uncompressed_gzip3(data):
        try:
            return gzip.decompress(data, 32 + gzip.MAX_WBITS) 
        except:
            return None
        
    def uncompressed_bz2(data):
        try:
            return bz2.decompress(data) 
        except:
            return None 

    def uncompressed_lzma(data):
        try:
            return lzma.decompress(data)
        except:
            return None 

    def uncompressed_codecs(data):
        try:
            return codecs.decode(data) 
        except:
            return None 

    def uncompressed_zipfile(data):
        try:
            with zipfile.ZipFile(data) as z:
                return z.read(z.namelist()[0]) 
        except:
            return None 

    def uncompressed_brotli(data):
        try:
            return brotli.decompress(data)
        except:
            return None 

    def uncompressed_binascii(data):
        try:
            return binascii.a2b_base64(data) 
        except:
            return None 

    def uncompressed_quopri(data):
        try:
            return quopri.decodestring(data) 
        except:
            return None

    def uncompressed_deflate(data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except:
            return None
    uncompressed_list = [
        (uncompressed_zlib, "uncompressed_zlib"),
        (uncompressed_gzip, "uncompressed_gzip"),
        (uncompressed_bz2, "uncompressed_bz2"),
        (uncompressed_lzma, "uncompressed_lzma"),
        (uncompressed_codecs, "uncompressed_codecs"),
        (uncompressed_zipfile, "uncompressed_zipfile"),
        (uncompressed_brotli, "uncompressed_brotli"),
        (uncompressed_binascii, "uncompressed_binascii"),
        (uncompressed_quopri, "uncompressed_quopri"),
        (uncompressed_deflate, "uncompressed_deflate"),
        (uncompressed_gzip2, "uncompressed_gzip2"),
        (uncompressed_gzip3, "uncompressed_gzip3"),
    ]

    def uncompressed_aes_with_key(data):
        try:
            key = base64.b64decode("VqfEhc6")
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
            return decrypted_data
        except Exception as e:
            print(Fore.RED + "AES decrypt failed:" +e + Style.RESET_ALL)
            return None
        
    def uncompressed_des_with_key(data):
        try:
            key = base64.b64decode("VqfEhc6")
            cipher = DES.new(key, DES.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(data), DES.block_size)
            return decrypted_data
        except Exception as e:
            print(Fore.RED + f"DES decrypt failed: {e}" + Style.RESET_ALL)
            return None

    def uncompressed_3des_with_key(data):
        try:
            key = base64.b64decode("VqfEhc6VqfEhc6VqfEhc6Vq")
            cipher = DES3.new(key, DES3.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(data), DES3.block_size)
            return decrypted_data
        except Exception as e:
            print(Fore.RED + f"3DES decrypt failed: {e}" + Style.RESET_ALL)
            return None

    def uncompressed_blowfish_with_key(data):
        try:
            key = base64.b64decode("VqfEhc6VqfEhc6Vq")
            cipher = Blowfish.new(key, Blowfish.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(data), Blowfish.block_size)
            return decrypted_data
        except Exception as e:
            print(Fore.RED + f"Blowfish decrypt failed: {e}" + Style.RESET_ALL)
            return None    
    unkey_list = [
            (uncompressed_aes_with_key, "uncompressed_aes_with_key"),
            (uncompressed_des_with_key, "uncompressed_des_with_key"),
            (uncompressed_3des_with_key, "uncompressed_3des_with_key"),
            (uncompressed_blowfish_with_key, "uncompressed_blowfish_with_key"),
            
        ]
    # print(Fore.GREEN + "start decoding..." + Style.RESET_ALL)
    # print(Fore.YELLOW + "source encoded_text:" + Style.RESET_ALL)
    # print(encoded_text)
    decode_stack = []
    parsed_route_set = set()
    save_result(encoded_text, [])

    def recursive_decode_stack(input_data, deepth=0, current_stack=None):
        if current_stack is None:
            current_stack = []
        
        if not decode_stack:
            yield  input_data, current_stack
        if deepth >= len(decode_stack):
            yield  input_data, current_stack
            return 
        else:
            yield input_data, current_stack
        
        for decode_func, func_name in decode_stack[deepth]:
            decode_data = decode_func(input_data)
            next_stack = current_stack.copy() + [(decode_func, func_name)]            
            #print(f"stack[{deepth}]: {func_name}")
            # print(Fore.CYAN + f"stack[{deepth}]: {func_name}" + Style.RESET_ALL)
            yield from recursive_decode_stack(decode_data, deepth + 1, next_stack)

    def decode_stack_push(input_encoded, func_name_list):
        nonlocal decode_stack
        success_list = []
        
        for pre_decode, current_stack in recursive_decode_stack(input_encoded):
            stack_str = " -> ".join([func_name for _, func_name in current_stack])
            
            # print(Fore.CYAN + f"stack: {stack_str}" + Style.RESET_ALL)
            for decode_func, func_name in func_name_list:
                try:
                    key = ".".join([f_name for _, f_name in current_stack] + [func_name]) 
                    if key in parsed_route_set:
                        continue
                    parsed_route_set.add(key)
                    # str -> bytes
                    decode_data = decode_func(pre_decode)
                    # print(Fore.GREEN +"Sucess:" + Style.RESET_ALL + f"{func_name}: {pre_decode} -> {decode_data}")
                    if not decode_data:
                        # print(f"func: {func_name} failed")
                        continue
                    func_stack = current_stack + [(decode_func, func_name)]
                    save_result(data=decode_data, stack=func_stack)
                    success_list.append((decode_func, func_name))
                except Exception as e:
                    # print(Fore.RED + f"error[{func_name}]:" + Style.RESET_ALL)
                    # print(e)
                    pass

        if success_list:
            decode_stack.append(success_list)
    def base_call(data, func):
        # missing_padding = len(data) % 8
        # if missing_padding:
        #     data += '=' * (8 - missing_padding)
        return func(data)
    
    base64_func_name_list = [(partial(base_call, func=getattr(base64, name)), name) for name in dir(base64) if 'decode' in name]
    decode_stack_push(encoded_text, base64_func_name_list)
    decode_stack_push(encoded_text, unkey_list)
    
    decode_stack_push(encoded_text, uncompressed_list)
    decode_stack_push(encoded_text, unkey_list)
    def decode_format(data, str_format):
        try:
            if not isinstance(data, bytes):
                data = data.encode()
            return codecs.decode(data, str_format)
        except BaseException as e:
            # print(e)
            return None
    str_format_list = ['utf8', 'utf16', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin1', 'ascii', 'unicode_escape',  'utf32', 'utf7', 'utf8', 'utf8_raw', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf8', 'utf8_raw', 'uu', 'zlib', "unicode_escape", 'unicode_internal']
    str_format_func_name_list = [((lambda data, str_format=str_format: decode_format(data, str_format)), str_format) for str_format in str_format_list]
    decode_stack_push(encoded_text, str_format_func_name_list)
    # decode_stack_push(encoded_text, str_format_func_name_list)



def decode_with_results(encoded_text: str) -> list:
    sucess_datas = set()
    sucess_results = []
    def save_result(data, stack):
        key = md5.md5(str(data).encode()).hexdigest()
        if key in sucess_datas:
            return
        sucess_datas.add(key)
        func_names = ",".join([func_name for _, func_name in stack])
        sucess_results.append((func_names, str(data)))
        
    decode(encoded_text, save_result)
    return sucess_results

datas = json.load(open("./analyze/searchlist.json"))["data"]["list"]
sucess_results = []
for i in range(len(datas)):
    encoded_text = datas[i]["bdjson"]
    results = decode_with_results(encoded_text)
    sucess_results.append(results)
first_result = sucess_results[0]
keys = [key for key, _ in first_result]
outputs =[list(item) for item in first_result]
for key, item in zip(keys, outputs):
    for i in range(1, len(sucess_results)):
        result = next(filter(lambda x: x[0] == key, sucess_results[i]), None)
        if result:
            item.append(result[1])
max_count = max([len(item) for item in outputs])
# filter not eq max_count
outputs = [item for item in outputs if len(item) == max_count]
    
    
filepath = "./analyze/decode_result.json"
# print(sucess_results)
content = json.dumps(outputs, indent=4, ensure_ascii=False)
with open(filepath, "w") as f:
    f.write(content)
print("save finish")