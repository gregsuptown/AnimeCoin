 
import sys, time, os.path, io, glob, hashlib, imghdr, random, os, zlib, pickle, sqlite3, uuid, socket, warnings, base64, json, hmac, logging, asyncio
#import bencode, crc32c, dht, krpc, tracker, utils #TinyBT
from shutil import copyfile
from random import randint
from math import ceil, log, floor, sqrt
from collections import defaultdict
from zipfile import ZipFile
from subprocess import check_output
from datetime import datetime
from kademlia.network import Server
#from pyp2p.net import *
#from pyp2p.unl import UNL
#from pyp2p.dht_msg import DHT
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    from fs.copy import copy_fs
    from fs.osfs import OSFS
try:
    from tqdm import tqdm
    import yenc
    import pyxolotl
except:
    pass
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair
#Requirements:
# pip install kademlia, pyxolotl, yenc, tqdm, fs

#Parameters:
use_start_new_network = 0
use_connect_to_existing_network = 0
use_register_local_blocks_on_dht = 1 
use_demonstrate_asking_network_for_file_blocks = 0
use_demonstrate_transferring_block_file_using_nat_upnp = 0
use_integrity_scan_of_block_files_on_startup = 0
folder_path_of_art_folders_to_encode = 'C:\\animecoin\\art_folders_to_encode\\' #Each subfolder contains the various art files pertaining to a given art asset.
block_storage_folder_path = 'C:\\animecoin\\art_block_storage\\'
chunk_db_file_path = 'C:\\animecoin\\anime_chunkdb.sqlite'

if use_integrity_scan_of_block_files_on_startup:
    if not os.path.exists(chunk_db_file_path):
        conn = sqlite3.connect(chunk_db_file_path)
        c = conn.cursor()
        local_hash_table_creation_string= """CREATE TABLE potential_local_hashes (block_hash text PRIMARY KEY, file_hash);"""
        global_hash_table_creation_string= """CREATE TABLE potential_global_hashes (
                                                block_hash text,
                                                file_hash text,
                                                peer_ip_and_port text,
                                                datetime_peer_last_seen text,
                                                PRIMARY KEY (block_hash,peer_ip_and_port)
                                                );"""
        c.execute(local_hash_table_creation_string)
        c.execute(global_hash_table_creation_string)
        conn.commit()
        
    potential_local_block_hashes_list = []
    potential_local_file_hashes_list = []
    list_of_block_file_paths = glob.glob(block_storage_folder_path+'*.block')
    print('Now Verifying Block Files ('+str(len(list_of_block_file_paths))+' files found)\n')
    
    try:
        pbar = tqdm(total=len(list_of_block_file_paths))
    except:
        print('.')
        
    for current_block_file_path in list_of_block_file_paths:
        with open(current_block_file_path, 'rb') as f:
            try:
                current_block_binary_data = f.read()
            except:
                print('\nProblem reading block file!\n')
                continue
        try:
            pbar.update(1)
        except:
            pass
        hash_of_block = hashlib.sha256(current_block_binary_data).hexdigest()
        reported_block_sha256_hash = current_block_file_path.split('\\')[-1].split('__')[-1].replace('BlockHash_','').replace('.block','')
        if hash_of_block == reported_block_sha256_hash:
            reported_file_sha256_hash = current_block_file_path.split('\\')[-1].split('__')[1]
            if reported_block_sha256_hash not in potential_local_block_hashes_list:
                potential_local_block_hashes_list.append(reported_block_sha256_hash)
                potential_local_file_hashes_list.append(reported_file_sha256_hash)
        else:
            print('\nBlock '+reported_block_sha256_hash+' did not hash to the correct value-- file is corrupt! Skipping to next file...\n')
    print('\n\nDone verifying block files!\nNow writing local block metadata to SQLite database...\n')
    table_name= 'potential_local_hashes'
    id_column = 'block_hash'
    column_name = 'file_hash'
    conn = sqlite3.connect(chunk_db_file_path)
    c = conn.cursor()
    c.execute("""DELETE FROM potential_local_hashes""")
    for hash_cnt, current_block_hash in enumerate(potential_local_block_hashes_list):
        current_file_hash = potential_local_file_hashes_list[hash_cnt]
        sql_string = """INSERT OR IGNORE INTO potential_local_hashes (block_hash, file_hash) VALUES (\"{blockhash}\", \"{filehash}\")""".format(blockhash=current_block_hash, filehash=current_file_hash)
        c.execute(sql_string)
    conn.commit()
    print('Done writing file hash data to SQLite file!\n')
    #list_of_local_potential_block_hashes = c.execute('SELECT block_hash FROM potential_local_hashes').fetchall()
    #set_of_local_potential_file_hashes = c.execute('SELECT DISTINCT file_hash FROM potential_local_hashes').fetchall()
    #conn.close()
    #list_of_block_file_paths = glob.glob(block_storage_folder_path+'*.block')
    #current_block_file_path = list_of_block_file_paths[0]


def generate_node_mac_hash_id():
    return hashlib.sha256(str(int(uuid.getnode())).encode('utf-8')).hexdigest()

def get_local_matching_blocks_from_file_hash_func(block_storage_folder_path,sha256_hash_of_desired_file):
    list_of_block_file_paths = glob.glob(os.path.join(block_storage_folder_path,'*'+sha256_hash_of_desired_file+'*.block'))
    list_of_block_hashes = []
    list_of_file_hashes = []
    for current_block_file_path in list_of_block_file_paths:
        reported_file_sha256_hash = current_block_file_path.split('\\')[-1].split('__')[1]
        list_of_file_hashes.append(reported_file_sha256_hash)
        reported_block_file_sha256_hash = current_block_file_path.split('__')[-1].replace('.block','').replace('BlockHash_','')
        list_of_block_hashes.append(reported_block_file_sha256_hash)
    return list_of_block_file_paths, list_of_block_hashes, list_of_file_hashes


try:
    list_of_block_file_paths, list_of_block_hashes, list_of_file_hashes = get_local_matching_blocks_from_file_hash_func(block_storage_folder_path,example_file_hash)
    example_block_hash_1 = list_of_block_hashes[0]
    example_block_hash_2 = list_of_block_hashes[1]
    example_file_hash_1 = list_of_file_hashes[0]
    example_file_hash_2 = list_of_file_hashes[1]
    example_block_file_path_hash_1 = list_of_block_file_paths[0]
    example_block_file_path_hash_2 = list_of_block_file_paths[0]
except:
    example_block_hash_1 = 'bb739b16f1e8bb3fe51f32c11319248649c18423c0c75bcaaae68bf4cb09cde0'
    example_block_hash_2 = 'f1126b528c10e97af98e1af71894e5a7a2d1dbf9ba30c94fff1f4d494e669ced'
    example_file_hash_1 = '7eb4b448d346b5bee36bba8b2a1e4983d64ac1a57c3064e39e93110c4704ef1b'
    example_file_hash_2 = '586e0ad859248b54e7c055028126bf22bc8a4850440c9829505ba9cf8164bba1'
    
default_port = 14142
alternative_port = 2718
bootstrap_node1 = ('108.61.86.243', int(default_port))
bootstrap_node2 = ('108.61.86.243', int(alternative_port))
bootstrap_node3 = ('140.82.14.38', int(default_port))
bootstrap_node4 = ('140.82.14.38', int(alternative_port))
bootstrap_node5 = ('140.82.2.58', int(default_port))
bootstrap_node6 = ('140.82.2.58', int(alternative_port))

bootstrap_node_list = [bootstrap_node1,bootstrap_node2,bootstrap_node3,bootstrap_node4,bootstrap_node5,bootstrap_node6]
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)   
my_node_id = generate_node_mac_hash_id()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
my_node_ip_address = s.getsockname()[0]
s.close()

bootstrap_node_list_filtered = [x for x in bootstrap_node_list if x[0] != my_node_ip_address]

conn = sqlite3.connect(chunk_db_file_path)
c = conn.cursor()
list_of_local_potential_block_hashes = c.execute('SELECT block_hash FROM potential_local_hashes').fetchall()
list_of_local_potential_block_hashes = [x[0] for x in list_of_local_potential_block_hashes]
list_of_local_potential_file_hashes = c.execute('SELECT file_hash FROM potential_local_hashes').fetchall()
list_of_local_potential_file_hashes = [x[0] for x in list_of_local_potential_file_hashes]
list_of_local_potential_block_hashes_json = json.dumps(list_of_local_potential_block_hashes)
list_of_local_potential_file_hashes_json = json.dumps(list_of_local_potential_file_hashes)
list_of_local_potential_file_hashes_unique = c.execute('SELECT DISTINCT file_hash FROM potential_local_hashes').fetchall()
list_of_local_potential_file_hashes_unique = [x[0] for x in list_of_local_potential_file_hashes_unique]
list_of_local_potential_file_hashes_unique_json = json.dumps(list_of_local_potential_file_hashes_unique)

def package_hash_table_entry_func(data_as_python_list):
    global default_port
    my_node_id = generate_node_mac_hash_id()
    data_as_python_list.insert(0,my_node_id)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        my_node_ip_address = s.getsockname()[0]
        s.close()
    except Exception as e:
        print('Error: '+ str(e)) 
    my_node_ip_and_port = my_node_ip_address+ ':' + str(default_port)
    data_as_python_list.insert(0,my_node_ip_and_port)
    data_as_json = json.dumps(data_as_python_list)
    data_as_json_zipped = zlib.compress(data_as_json.encode('utf-8'))
    _, _, data_as_json_zipped_yenc_encoded = yenc.encode(data_as_json_zipped)
    #print(data_as_json_zipped_yenc_encoded.decode('unicode-escape'))
    return data_as_json_zipped_yenc_encoded

    use_demonstrate_size_of_encodings = 0
    if use_demonstrate_size_of_encodings:
        data_as_json_zipped_base64_encoded = base64.b64encode(data_as_json_zipped)
        size_of_data_as_json = sys.getsizeof(data_as_json)
        size_of_data_as_json_zipped = sys.getsizeof(data_as_json_zipped)
        size_of_data_as_json_zipped_yenc_encoded = sys.getsizeof(data_as_json_zipped_yenc_encoded)
        size_of_data_as_json_zipped_base64_encoded = sys.getsizeof(data_as_json_zipped_base64_encoded)
        with open('data_as_json','wb') as f:
            f.write(data_as_json.encode('utf-8'))
        with open('data_as_json_zipped','wb') as f:
            f.write(data_as_json_zipped)   
        with open('data_as_json_zipped_yenc_encoded','wb') as f:
            f.write(data_as_json_zipped_yenc_encoded)
        with open('data_as_json_zipped_base64_encoded','wb') as f:
            f.write(data_as_json_zipped_base64_encoded)    
        print('Comparison of the size of different representations of the data:\n')
        print('data_as_json: '+str(size_of_data_as_json))
        print('data_as_json_zipped: '+str(size_of_data_as_json_zipped))
        print('data_as_json_zipped_yenc_encoded: '+str(size_of_data_as_json_zipped_yenc_encoded))
        print('data_as_json_zipped_base64_encoded: '+str(size_of_data_as_json_zipped_base64_encoded))
        print('Now verifying that we can decode the Yenc text and then unzip the data to get the original json:')
        _, _, yenc_decoded = yenc.decode(data_as_json_zipped_yenc_encoded)
        data_as_json_unzipped = zlib.decompress(yenc_decoded)
        if yenc_decoded == data_as_json_zipped:
            print('Decoded the Yenc successfully!')
        if data_as_json_unzipped == data_as_json.encode('utf-8'):
            print('Unzipped the data successfully!')


def unpackage_hash_table_entry_func(data_as_yenc_encoded_zipped_data):
    _, _, yenc_decoded = yenc.decode(data_as_yenc_encoded_zipped_data)
    data_as_json_unzipped = zlib.decompress(yenc_decoded)
    data_as_list_with_headers = json.loads(data_as_json_unzipped)
    node_ip_and_port = data_as_list_with_headers[0]
    node_ip = node_ip_and_port.split(':')[0]
    node_port = int(node_ip_and_port.split(':')[1])
    node_id = data_as_list_with_headers[1]
    data_as_list = data_as_list_with_headers[2:]
    return data_as_list, node_ip, node_port, node_id

if 0:#Example usage:
    yencoded_zipped_json = package_hash_table_entry_func(block_hash_list)
    data_as_list, node_ip, node_port, node_id = unpackage_hash_table_entry_func(yencoded_zipped_json)

def get_blocks_for_given_file_hash_func(file_hash):
    global chunk_db_file_path
    conn = sqlite3.connect(chunk_db_file_path)
    c = conn.cursor()
    blocks_for_this_file_hash = c.execute("""SELECT block_hash FROM potential_local_hashes where file_hash = ?""",[file_hash]).fetchall()
    list_of_block_hashes = []
    for current_block in blocks_for_this_file_hash:
        list_of_block_hashes.append(current_block[0])
    list_of_block_hashes_json = json.dumps(list_of_block_hashes)
    return list_of_block_hashes

def advertise_local_blocks_to_network(server):
    global default_port
    global alternative_port
    global list_of_local_potential_block_hashes
    global list_of_local_potential_file_hashes
    global list_of_local_potential_file_hashes_unique
    
    for cnt, current_file_hash in enumerate(list_of_local_potential_file_hashes_unique):
        list_of_block_hashes = get_blocks_for_given_file_hash_func(current_file_hash)
        yencoded_zipped_json = package_hash_table_entry_func(list_of_block_hashes)
        try:
            print('Broadcasting to the network the list of blocks for the zip file with hash: '+current_file_hash)
            asyncio.get_event_loop().run_until_complete(server.set(current_file_hash,yencoded_zipped_json))
            time.sleep(1)
        except:
            pass
        
def ask_network_for_blocks_corresponding_to_hash_of_given_zipfile_func(server,sha256_hash_of_desired_zipfile):
    try:
        print('\nAsking network for any block hashes that correspond to the zip file with the SHA256 hash: '+sha256_hash_of_desired_zipfile+'\n')
        yencoded_zipped_json = asyncio.get_event_loop().run_until_complete(server.get(sha256_hash_of_desired_zipfile))
        time.sleep(5)
        data_as_list, node_ip, node_port, node_id = unpackage_hash_table_entry_func(yencoded_zipped_json)
        return data_as_list, node_ip, node_port, node_id
    except:
        pass

def start_new_network_func(port):
    try:
        server = Server()
        server.listen(port)
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()
            loop.close()
    except Exception as e:
        print('Error: '+ str(e))

def connect_to_existing_network(port):
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        server = Server()
        server.listen(port)
        return server, loop
    except Exception as e:
        print('Error: '+ str(e))

if use_start_new_network:
    start_new_network_func(alternative_port)  

if use_connect_to_existing_network:
    server, loop = connect_to_existing_network(default_port)
    print('Bootstrapping network now!\n')
    loop.run_until_complete(server.bootstrap(bootstrap_node_list_filtered))
    time.sleep(10)
    
    if use_register_local_blocks_on_dht:
        advertise_local_blocks_to_network(server)
        
    if use_demonstrate_asking_network_for_file_blocks:
        #test_file_hash = 'a75a1757d54ad0876f9b2cf9b64b1017b6293ceed61e80cd64aae5abfdc8514e' #Arturo_number_04
        #test_file_hash = '734ad8214cb20deab6474f19397d012678de4acc61c4c24de35ce3b8cc466d5f' #Mark_Kong_number_02
        test_file_hash = '105c4c9b9d79ed544c36df792f7bbbddb6700209f51e4b9e1073fa41653d2aa8' #Iris Madula Number 11
        
        print('Now asking network for hashes of blocks that correspond to the zipfile with a SHA256 hash of: '+test_file_hash)
        list_of_block_hashes, remote_node_ip, remote_node_port, remote_node_id = ask_network_for_blocks_corresponding_to_hash_of_given_zipfile_func(server,test_file_hash)
        print('\n\nDone! Got back '+str(len(list_of_block_hashes))+' Block Hashes:\n')
        print('\nNode IP:port is '+remote_node_ip+':'+str(remote_node_port))
        print('\nNode ID is '+remote_node_id+'\n\n')
        for current_block_hash in list_of_block_hashes:
            print(current_block_hash+', ',end='')

    if use_demonstrate_transferring_block_file_using_nat_upnp:
         _, my_node_ip, my_node_port, my_node_id = unpackage_hash_table_entry_func( package_hash_table_entry_func([]))
        
    if 0: #Experiments with PyP2P:
        my_dht = DHT()
        my_node_direct = Net(passive_bind=my_node_ip, passive_port=my_node_port, net_type='p2p', dht_node=my_dht, debug=1)
        my_node_direct.start()
        remote_dht = DHT()
        remote_node_direct = Net(passive_bind=remote_node_ip, passive_port=remote_node_port, net_type='p2p', dht_node=remote_dht, debug=1)
        remote_node_direct.start()
        my_node_direct.unl.connect(bob_direct.unl.construct(), events)

        

if 0:
    loop.call_soon_threadsafe(loop.stop)
    server.stop()
    loop.close()

