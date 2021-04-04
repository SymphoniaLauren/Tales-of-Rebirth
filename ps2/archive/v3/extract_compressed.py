import os, sys, json, shutil, subprocess, struct

def is_compressed(data):
    if (data[0] == 1) or (data[0] == 3):
        if struct.unpack('<L', data[1:5])[0] == len(data) - 9:
            return [True, data[0]]
    return [False]


def extract_compressed():
    try: os.mkdir('FILE')
    except: pass
    
    json_file = open('compressed.json', 'w')
    json_data = {}
    
    for name in os.listdir('dat'):
        f = open('dat/' + name, 'rb')
        data = f.read()
        f.close()
        compressed_data = is_compressed(data)
        if compressed_data[0] == False:
            continue
        print ("EXTRACTING " + name)
        json_data[name] = compressed_data[1]
        filename = 'file/' + name
        shutil.copy('dat/' + name, filename)
        subprocess.run(['comptoe', '-d', filename, filename + '.d'])
        os.remove(filename)
        f = open(filename + '.d', 'rb')
        data = f.read()
        f.close()
        if data[:4] == b'TIM2':
            json_data[name] = 'tim2'
        os.rename(filename + '.d', filename)
        
    json.dump(json_data, json_file, indent=4)
    

def check():
    json_file = open('compressed.json', 'w')
    json_data = {}
    
    for name in os.listdir('file'):
        f = open('file/' + name, 'rb')
        data = f.read()
        f.close()
        if data[:4] == b'TIM2':
            json_data[name] = 'tim2'
        #elif is_pak0(data):
        #    json_data[name] = 'pak0'
        #else:
        #    pass
    print ("checking")
        
    json.dump(json_data, json_file, indent=4)
    
if __name__ == '__main__':
    extract_compressed()
    check()
