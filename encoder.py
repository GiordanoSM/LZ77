import sys
import re
import time

def main():

  header = b'FA'
  
  filename = input("Informe o nome (caminho) do arquivo a ser comprimido: ")
  directory = input("Informe o nome do diretório do resultado (será o atual caso não informado): ")

  no_path_name = remove_path(filename)
  filename_result = add_path_bin(directory, no_path_name)

  try:
    with open(filename, 'rb') as f_read:
      with open(filename_result, 'wb') as f_write:
        f_write.write(header)
        encode(f_read, f_write)

  except IOError as ioe:
    sys.exit('Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  print("Finished!\n")

#--------------------------------------

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_bin(directory, no_path_name):
  bin_name = no_path_name + '.bin'
  return directory + '/' + bin_name if directory else bin_name

def encode(f_read, f_write):
  #result = []

  print('Enconding... (this may take a while)')
  start = time.time()

  if len(sys.argv) > 1:
    search_buffer_max = sys.argv[1]
  else:
    search_buffer_max = 8

  search_buffer = []

  if len(sys.argv) > 2:
    look_ahead_buffer_max = sys.argv[2]
  else:
    look_ahead_buffer_max = 7

  look_ahead_buffer = []

  f_bytes = f_read.read(7)

  look_ahead_buffer = list(f_bytes)

  while(f_bytes or len(look_ahead_buffer) > 0):

    triple = find_pattern(search_buffer, look_ahead_buffer)

    next_s = triple[1] + 1

    f_bytes = f_read.read(next_s)

    if len(search_buffer) + next_s <= search_buffer_max:

      search_buffer = search_buffer + look_ahead_buffer[:next_s]

    else: 
      #Esperasse que com o tempo seja diff = next_s
      diff = len(search_buffer) - search_buffer_max + next_s #Diff maior que zero devido à condição do if

      search_buffer = search_buffer[diff:] + look_ahead_buffer[:next_s]

    look_ahead_buffer = look_ahead_buffer[next_s:] + list(f_bytes)

    f_write.write(triple[0].to_bytes(1, byteorder='big') + triple[1].to_bytes(1, byteorder= 'big') + triple[2])
    
    #result.append(triple)

  end = time.time()
  print('Demorou: {} segundos'.format(end - start))
  #print(result)


def find_pattern(search_buffer, look_ahead_buffer):

  best_result = (0,0, look_ahead_buffer[0].to_bytes(1, byteorder='big'))

  sb_size = len(search_buffer)
  lab_size = len(look_ahead_buffer)

  for sb_i in range(sb_size):

    if search_buffer[sb_i] == look_ahead_buffer[0] and lab_size > 1:

      seq_i = sb_i + 1
      la_i = 1
      # -1 para n incluir o ultimo termo no casamento
      while (seq_i < sb_size
            and la_i < lab_size - 1
            and search_buffer[seq_i] == look_ahead_buffer[la_i]):
        seq_i += 1
        la_i += 1

      if seq_i == sb_size:
        while (la_i < lab_size - 1
              and look_ahead_buffer[seq_i - sb_size] == look_ahead_buffer[la_i]):
          seq_i += 1
          la_i += 1

      if seq_i - sb_i > best_result[1]:
        best_result = (sb_size - sb_i, seq_i - sb_i, look_ahead_buffer[la_i].to_bytes(1, byteorder='big'))

  return best_result

if __name__ == "__main__":
  main()