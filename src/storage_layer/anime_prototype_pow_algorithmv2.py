import os, time, hashlib, math
from time import sleep
from tqdm import tqdm
from decimal import getcontext, Decimal
from math import floor, log

def convert_integer_to_bytes_func(input_integer):
    if input_integer == 0:
        return b''
    else: #Uses recursion:
        return convert_integer_to_bytes_func(input_integer//256) + bytes([input_integer%256])

def check_that_all_block_transactions_are_valid_func(block_transaction_data):
    if 1==1:  # This is just a placeholder function
        all_transactions_are_valid = 1
    else:
        all_transactions_are_valid = 0
    return all_transactions_are_valid

def generate_block_candidate_func(block_transaction_data, nonce_number):
    nonce = convert_integer_to_bytes_func(nonce_number)
    block_transaction_data_with_nonce = block_transaction_data + nonce
    if USE_VERBOSE:
        print('Generated new block candidate for nonce: '+ str(nonce_number))
    return block_transaction_data_with_nonce

def get_hash_list_func(block_transaction_data_with_nonce, use_verbose): #Adjusted so each has the same length
    hash_01 = hashlib.sha256(block_transaction_data_with_nonce).hexdigest() + hashlib.sha256(block_transaction_data_with_nonce).hexdigest()
    hash_02 = hashlib.sha3_256(block_transaction_data_with_nonce).hexdigest() + hashlib.sha3_256(block_transaction_data_with_nonce).hexdigest()
    hash_03 = hashlib.sha3_512(block_transaction_data_with_nonce).hexdigest()
    hash_04 = hashlib.blake2s(block_transaction_data_with_nonce).hexdigest() + hashlib.blake2s(block_transaction_data_with_nonce).hexdigest()
    hash_05 = hashlib.blake2b(block_transaction_data_with_nonce).hexdigest()
    hash_list = [hash_01, hash_02, hash_03, hash_04, hash_05]
    if use_verbose:
        list_of_hash_types = ['SHA-256 + (Repeated again in reverse)', 'SHA3-256 + (Repeated again in reverse)', 'SHA3-512', 'BLAKE2S + (Repeated again in reverse)', 'BLAKE2B']
        print('\n\nList of computed hashes:\n')
        for hash_count, current_hash in enumerate(hash_list):
            print(list_of_hash_types[hash_count]+ ': ' + current_hash)
    return hash_list

def digits_in_number_func(x):
    try:
        return int(math.log10(x)) + 1
    except:
        return int(math.log10(-x)) + 1

def check_score_of_hash_list_func(input_hash_list, difficulty_level, baseline_number_of_digits_in_combined_hash, use_verbose):
    combined_hash = 0
    hash_list_score = 0
    list_of_hash_integers = list()
    for current_hash in input_hash_list:
        list_of_hash_integers.append(Decimal(int(current_hash, 16)))
    list_of_hashes_in_size_order = sorted(list_of_hash_integers)
    smallest_hash = list_of_hashes_in_size_order[0]
    second_smallest_hash = list_of_hashes_in_size_order[1]
    middle_hash = list_of_hashes_in_size_order[2]
    second_largest_hash = list_of_hashes_in_size_order[-2]
    largest_hash = list_of_hashes_in_size_order[-1]
    combined_hash_step_1 = (pow(largest_hash, 5) / pow(second_largest_hash, 3))/(Decimal(10)*largest_hash.log10()*smallest_hash.log10())
    combined_hash_step_2 = (pow(middle_hash, 5) / pow(second_smallest_hash, 3))/(Decimal(10)*second_largest_hash.log10()*second_smallest_hash.log10())
    combined_hash_step_3 = (pow(second_largest_hash, 5) / pow(smallest_hash, 3))/(Decimal(10)*largest_hash.log10()*middle_hash.log10()*smallest_hash.log10())
    combined_hash = int(floor( (combined_hash_step_1*combined_hash_step_2*combined_hash_step_3)/(Decimal(10)*max([combined_hash_step_1, combined_hash_step_2, combined_hash_step_3])) ))
    combined_hash_hex = str(hex(combined_hash)).replace('0x','')
    number_of_digits_in_combined_hash = digits_in_number_func(combined_hash)
    if number_of_digits_in_combined_hash <= (baseline_number_of_digits_in_combined_hash - difficulty_level):
        hash_list_score = 1
    if USE_VERBOSE:
        print('Step 1: ' + str(combined_hash_step_1))
        print('Step 2: ' + str(combined_hash_step_2))
        print('Step 3: ' + str(combined_hash_step_3))
        print('Combined Hash as Integer: ' + str(combined_hash))
        print('Combined Hash in Hex: ' + combined_hash_hex)
    return hash_list_score, combined_hash, combined_hash_hex, number_of_digits_in_combined_hash
def mine_for_new_block_func(block_transaction_data, difficulty_level, block_count, baseline_number_of_digits_in_combined_hash):
    start_time = time.time()
    pbar = tqdm()
    block_is_valid = 0
    nonce_number = 0
    all_transactions_are_valid = check_that_all_block_transactions_are_valid_func(block_transaction_data)
    if all_transactions_are_valid:
        while block_is_valid == 0:
            pbar.update(1)
            nonce_number = nonce_number + 1
            block_transaction_data_with_nonce = generate_block_candidate_func(block_transaction_data, nonce_number)
            current_hash_list = get_hash_list_func(block_transaction_data_with_nonce, use_verbose=USE_VERBOSE)
            current_hash_list_score, current_combined_hash, combined_hash_hex, number_of_digits_in_combined_hash = check_score_of_hash_list_func(current_hash_list, difficulty_level, baseline_number_of_digits_in_combined_hash, use_verbose=USE_VERBOSE)
            if nonce_number == 1:
                current_best_combined_hash = current_combined_hash
            if current_combined_hash < current_best_combined_hash:
                current_best_combined_hash = current_combined_hash
                current_best_combined_hash_hex = combined_hash_hex
                pbar.set_description('Best combined hash so far: ' + current_best_combined_hash_hex)
            if current_hash_list_score >= MIN_HASH_LIST_SCORE:
                end_time = time.time()
                block_duration_in_minutes = (end_time - start_time)/60
                try:
                    current_best_combined_hash_hex
                except NameError:
                    current_best_combined_hash_hex = hex(0)
                print('\n\n\n\n***Just mined a new block!***\n\n Block Duration: '+str(round(block_duration_in_minutes,3))+' minutes.\n\n')
                print('Block Number: ' + str(block_count))
                print('Hash of mined block: '+ current_best_combined_hash_hex)
                print('Hash as integer: '+str(int(current_best_combined_hash_hex,16))+'\n')
                print('Number of Digits in Integer Hash: '+str(len(str(int(current_best_combined_hash_hex,16))))+'\n')
                print('Individual Hash Values SHA-256 (Repeated 2x), SHA3-256 (Repeated 2x), SHA3-512, BLAKE2S (Repeated 2x), and BLAKE2B, respectively:\n')
                for current_hash in current_hash_list:
                    print(current_hash)
                print('Applying the following transformations to individual hashes to generate the combined hash:\n')
                print(FORMULAS_STRING)
                print('\nCurrent Difficulty Level: ' + str(difficulty_level))
                print('\nCurrent Number of Digits of Precision: '+str(getcontext().prec))
                print('Sleeping for 3 seconds...')
                sleep(3)
                return current_hash_list, current_hash_list_score, current_combined_hash, combined_hash_hex,  block_duration_in_minutes

try:
  block_count
except NameError:
  block_count = 1
use_demo = 1
number_of_demo_blocks_to_mine = 500
USE_VERBOSE = 0
MIN_HASH_LIST_SCORE = 1
baseline_digits_of_precision = 10
getcontext().prec = baseline_digits_of_precision
current_required_number_of_digits_of_precision = baseline_digits_of_precision
number_of_digits_of_precision = baseline_digits_of_precision
max_digits_of_precision = 1000 #How many digits we want to keep track of in the decimal expansion of numbers
increase_hash_difficulty_every_k_blocks = 10
reset_numerical_precision_every_r_blocks = increase_hash_difficulty_every_k_blocks
startup_period_in_number_of_blocks = 2
max_difficulty_increase_per_block = 1
difficulty_level = 1 #Starting level
target_block_duration_in_minutes = 1
FORMULAS_STRING = """\nlist_of_hash_integers = list()
                        for current_hash in input_hash_list:
                            list_of_hash_integers.append(Decimal(int(current_hash, 16)))
                        list_of_hashes_in_size_order = sorted(list_of_hash_integers)
                        smallest_hash = list_of_hashes_in_size_order[0]
                        second_smallest_hash = list_of_hashes_in_size_order[1]
                        middle_hash = list_of_hashes_in_size_order[2]
                        second_largest_hash = list_of_hashes_in_size_order[-2]
                        largest_hash = list_of_hashes_in_size_order[-1]
                        combined_hash_step_1 = (pow(largest_hash, 5) / pow(second_largest_hash, 3))/(Decimal(10)*largest_hash.log10()*smallest_hash.log10())
                        combined_hash_step_2 = (pow(middle_hash, 5) / pow(second_smallest_hash, 3))/(Decimal(10)*second_largest_hash.log10()*second_smallest_hash.log10())
                        combined_hash_step_3 = (pow(second_largest_hash, 5) / pow(smallest_hash, 3))/(Decimal(10)*largest_hash.log10()*middle_hash.log10()*smallest_hash.log10())
                        combined_hash = int(floor( (combined_hash_step_1*combined_hash_step_2*combined_hash_step_3)/(Decimal(1/100)*max([combined_hash_step_1, combined_hash_step_2, combined_hash_step_3])) ))
                        combined_hash_hex = str(hex(combined_hash)).replace('0x','')"""

ascii_art = """
               _,u-*P"9\w__     __..e-w.__
            _a*^          ^w.e*'"_____   `*mw____
          _wP               'm_m^"   "'*L    ""~~*vL__
        _gK                   5L         Y,          "*x,_
      _u@0'                ___ #          1             "^m_
   _a*"  0               _#" ^LjL         7     gL         `#r--x,_
  a@"    b              gK    `@P         7   ,#"#           \_  "^w
 jP      0              0                 #  d"  Mr            ",   9w
 #       0              #                aE,P    `#              #,  *#w
JF       0,      a+     #                ""       7L              9,   "g_
#         #,  _q#"     0"                          #               9_    Q
#          "mP"0"  _,rP                            'Q             __7w   0
#_             ""'""~                                *w             P#MW  E
JF                                                   #               ?L  *K
 #_                                                  0                 aw#
  7L                           ,,   _     _          *,         __       #'
   7L                       _,g@_.adK _,m*#           1         #^6,     5_
    !w_                 __g#6w##5MM@gK5,,# _w  ,      1        g'  9,     0
      9w,              gM"@M5  "*u,_   _#m+_# ##__    S_      _#   JFam,  5
        "\w__  _   ___ # g'0  _.wgM#'     _0w# J#@W    0x_  _J@     ## '# d
           ""-*#Kr-#K# # 0_0 q@ "#JK      d#M  7#&}L     "--P       J#r 9g#
                0_JF## # "P#w_ pMa#      ""  a  a_"0#               jF   d"
                J& M_# #     "PP9        ,p g1    WgMQ             a#L _#"
                 AK "# #                ,   #  a#mC#9#            d'JL/"
                  Am## #                '   "^m_dWP  9w   am    a#~ -"
                  J#'# 7_               P   9m ""~ _m"_wr"\# _pP'"
                  MF # #Mw           q_          _#"   j#m^
                __0L.JL!K_&_         _          J#       "
              .*""~____#_# "^w_      *~        uK]#L
               #*^"   9K0w--4#w             _0'  ##
               #       Q #    `*m_ ____.w-*^"    ]M#
              g"       !W0       *#0ME            9MQ
                        0M,       40J&             `WQ_
                         0#                          0M_
                         0#,                          X#,
                         *W1                           A#,
                          #Q                            3#,
                          0#                             ]#
                          0#                             JP
                          3#                                """
if use_demo:
    if block_count==1:
        if block_count <= startup_period_in_number_of_blocks:
            max_precision_increase_per_iteration = 5
        print('***WELCOME TO ANIMECOIN POW***')
        print(ascii_art)
        print('Generating fake transaction data for block...')
        block_transaction_data = os.urandom(pow(10,5))
        block_transaction_data_with_nonce = generate_block_candidate_func(block_transaction_data, block_count)
        sample_hash_list = get_hash_list_func(block_transaction_data_with_nonce, use_verbose=0)
        _, _, _, baseline_number_of_digits_in_combined_hash = check_score_of_hash_list_func(sample_hash_list, difficulty_level=1, baseline_number_of_digits_in_combined_hash=500, use_verbose=0)
        print('Initial Block Difficulty: '+ str(difficulty_level))
        print('Initial Number of decimal places of accuracy: '+str(baseline_digits_of_precision))
        print('Target block duration in minutes: '+str(target_block_duration_in_minutes))
        print('Sleeping for 3 seconds...')
        sleep(3)
    for ii in range(number_of_demo_blocks_to_mine):
        current_hash_list, current_hash_list_score, current_combined_hash, current_combined_hash_hex,  current_block_duration_in_minutes = mine_for_new_block_func(block_transaction_data, difficulty_level, block_count, baseline_number_of_digits_in_combined_hash)
        block_count = block_count + 1
        ratio_of_actual_block_time_to_target_block_time = target_block_duration_in_minutes/current_block_duration_in_minutes
        print('Ratio of actual block time to target block time: '+ str(ratio_of_actual_block_time_to_target_block_time))
        getcontext().prec = current_required_number_of_digits_of_precision
        if ratio_of_actual_block_time_to_target_block_time > 1: #Block size was too short; increase difficulty and numerical precision:
            current_required_number_of_digits_of_precision = floor(current_required_number_of_digits_of_precision*min([(1 + max_precision_increase_per_iteration), ratio_of_actual_block_time_to_target_block_time]))
            if block_count > startup_period_in_number_of_blocks:
                max_precision_increase_per_iteration = log(max_digits_of_precision/current_required_number_of_digits_of_precision)/log(increase_hash_difficulty_every_k_blocks - startup_period_in_number_of_blocks) # X% increase per round, so final precision will be ~ final_digits_of_precision digits
            if reset_numerical_precision_every_r_blocks%block_count==0:
                current_required_number_of_digits_of_precision = baseline_digits_of_precision
            if increase_hash_difficulty_every_k_blocks%block_count==0:
                computed_difficulty_level_increase = floor(min([ratio_of_actual_block_time_to_target_block_time, max_difficulty_increase_per_block]))
            else:
                computed_difficulty_level_increase = 0
        else: #Block size was too long; reduce difficulty and numerical precision:
            current_required_number_of_digits_of_precision = floor(current_required_number_of_digits_of_precision*max([(1 - max_precision_increase_per_iteration), ratio_of_actual_block_time_to_target_block_time]))
            if block_count > startup_period_in_number_of_blocks:
                max_precision_increase_per_iteration = log(current_required_number_of_digits_of_precision/max_digits_of_precision)/log(increase_hash_difficulty_every_k_blocks - startup_period_in_number_of_blocks) # X% decrease per round, so final precision will be ~ final_digits_of_precision digits
            if reset_numerical_precision_every_r_blocks%block_count==0:
                current_required_number_of_digits_of_precision = baseline_digits_of_precision
            if increase_hash_difficulty_every_k_blocks%block_count==0:
                computed_difficulty_level_increase = floor(max( [(1/ratio_of_actual_block_time_to_target_block_time), -max_difficulty_increase_per_block]) )
            else:
                computed_difficulty_level_increase = 0
        getcontext().prec = current_required_number_of_digits_of_precision
        print('Increasing required numerical precision by '+ str(round(100*computed_difficulty_level_increase))+'% for next block.\n\n')
        difficulty_level = difficulty_level + computed_difficulty_level_increase

use_debug_mode = 1
if use_debug_mode:
    block_is_valid = 0
    nonce_number = 0
    block_transaction_data = os.urandom(pow(10,5))
    block_transaction_data_with_nonce = generate_block_candidate_func(block_transaction_data, nonce_number)
    current_hash_list = get_hash_list_func(block_transaction_data_with_nonce, use_verbose=USE_VERBOSE)
    input_hash_list = current_hash_list
