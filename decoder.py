import sys
import re

def main():
  header = b'FA'
  
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

  print("Finished!\n")

#-----------------------------

class WrongHeader(Exception):
  pass

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_rmv_bin(directory, no_path_name):
  no_bin_name = no_path_name[:-4]
  return directory + '/' + no_bin_name if directory else no_bin_name

def decode(f_read, f_write):

  search_buffer = []
  search_buffer_max = 8

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

    print(search_buffer)

if __name__ == "__main__":
  main()