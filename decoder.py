import sys
import re
import time
import bitstring as bs

def main():
  header = bs.Bits(hex='0xF0') #Header sendo F + numero de bits de padding no final do arquivo
  
  filename = input("Informe o nome (caminho) do arquivo a ser descomprimido: ")
  directory = input("Informe o nome do diretório do resultado (será o atual caso não informado): ")

  no_path_name = remove_path(filename)
  filename_result = add_path_rmv_bin(directory, no_path_name)

  if no_path_name[-4:] != '.bin':
    sys.exit('Erro: Esperado arquivo de extensão: ".bin".')

  try:
    with open(filename, 'rb') as f_read:
      with open(filename_result, 'wb') as f_write:
        header = f_read.read(2)

        if header != b'FA':
          raise WrongHeader

        decode(f_read, f_write)

  except IOError as ioe:
    sys.exit('Erro: Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  except WrongHeader:
    sys.exit('Erro: Header do arquivo não condiz com o esperado.')

  print("Terminado! Criado arquivo {}.\n".format(filename_result))

#-----------------------------

class WrongHeader(Exception):
  pass

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_rmv_bin(directory, no_path_name):
  no_bin_name = no_path_name[:-4]
  return directory + '/' + no_bin_name if directory else no_bin_name

def decode(f_read, f_write):
  print('Decoding... (this may take a while)')
  start = time.time()

  if len(sys.argv) > 1:
    search_buffer_max = min(int(sys.argv[1]), 255)
  else:
    search_buffer_max = 16

  search_buffer = []

  triple = tuple(f_read.read(3))
  
  while(triple):

    index = triple[0]
    size = triple[1]

    if index > 0 and size > 0:
      index = len(search_buffer) - index

      for i in range(size):
        search_buffer.append(search_buffer[index + i])
        f_write.write(search_buffer[index + i])
      
      if len(search_buffer) > search_buffer_max:
        search_buffer = search_buffer[len(search_buffer) - search_buffer_max:]

    if len(search_buffer) == search_buffer_max:
      search_buffer.pop(0)

    search_buffer.append(triple[2].to_bytes(1, byteorder= 'big'))
    f_write.write(triple[2].to_bytes(1, byteorder= 'big'))

    triple = tuple(f_read.read(3))
  
  end = time.time()
  print('Demorou: {} segundos'.format(end - start))

    #print(search_buffer)

if __name__ == "__main__":
  main()