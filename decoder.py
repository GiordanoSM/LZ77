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
    with open(filename_result, 'wb') as f_write:
      bits_header = bs.Bits(filename= filename, length= 8) #Lê o primeiro byte do arquivo
      
      padding = check_header(bits_header) #Retira as informações do header

      file_bin = bs.Bits(filename= filename, offset= 8) #Lê o resto do arquivo (Isso não traz para a memória o arquivo todo de uma vez)

      decode(file_bin, f_write, padding)

  except IOError as ioe:
    sys.exit('Erro: Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  except WrongHeader:
    sys.exit('Erro: Header do arquivo não condiz com o esperado.')

  print("Terminado! Criado arquivo '{}'.\n".format(filename_result))

#-----------------------------

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_rmv_bin(directory, no_path_name):
  no_bin_name = no_path_name[:-4]
  return directory + '/' + no_bin_name if directory else no_bin_name

def decode(file_bin, f_write, padding):
  print('Decodificando... (pode demorar)')
  start = time.time()

  if len(sys.argv) > 1:
    search_buffer_max = min(int(sys.argv[1]), 255)
  else:
    search_buffer_max = 16

  search_buffer = []

  end = file_bin.len - padding #Id do final do arquivo

  buffer = bs.Bits(bin= '0b')
  
  count = 0
  while count < end:

    triple = file_bin[count:count + 24]
    count = count + 24

    index = triple[0:8].uint
    size = triple[8:16].uint
    next_s = triple[16:].tobytes()

    if index > 0 and size > 0:
      index = len(search_buffer) - index

      for i in range(size):
        search_buffer.append(search_buffer[index + i])
        f_write.write(search_buffer[index + i])
      
      if len(search_buffer) >= search_buffer_max:
        search_buffer = search_buffer[len(search_buffer) - search_buffer_max + 1:]

    elif len(search_buffer) == search_buffer_max:
      search_buffer.pop(0)

    search_buffer.append(next_s)
    f_write.write(next_s)
  
  end = time.time()
  print('Demorou: {} segundos'.format(end - start))

  #print(search_buffer)

def check_header(header):

  if header[:-4] == bs.Bits(hex= '0xf'):
    return header[4:].uint

  else: raise WrongHeader

class WrongHeader(Exception):
  pass

if __name__ == "__main__":
  main()