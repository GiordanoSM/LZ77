import sys
import re
import time
import bitstring as bs
import my_huffman as mh

def main():  
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

      _list = bs.Bits(filename= filename, offset= 8,  length= 256) #Lê os 256 bits que indicam os símbolos (Huffman)
      list_symbols = get_symbols(_list) #Extrai quais são os símbolos (Huffman)

      bits_lengths = bs.Bits(filename= filename, offset= 264, length= len(list_symbols)*8) #Lê os tamanhos dos códigos (Huffman)
      lengths = get_lengths(bits_lengths) #Extrai os tamanhos dos códigos (Huffman)

      file_bin = bs.Bits(filename= filename, offset= 264 + len(list_symbols)*8) #Lê o resto do arquivo (Isso não traz para a memória o arquivo todo de uma vez)

      decode(file_bin, f_write, padding, list_symbols, lengths)

  except IOError as ioe:
    sys.exit('Erro: Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  except WrongHeader:
    sys.exit('Erro: Header do arquivo não condiz com o esperado.')

  print("Terminado! Criado arquivo '{}'.\n".format(filename_result))

#-----------------------------

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

#----------------------------
def add_path_rmv_bin(directory, no_path_name):
  no_bin_name = no_path_name[:-4]
  return directory + '/' + no_bin_name if directory else no_bin_name

#-----------------------------
def decode(file_bin, f_write, padding, list_symbols, lengths):
  print('Decodificando... (pode demorar)')
  start = time.time()

  if len(sys.argv) > 1:
    search_buffer_max = min(int(sys.argv[1]), 255)
  else:
    search_buffer_max = 16

  search_buffer = []

  code, tree = mh.gen_code_tree(list_symbols, lengths)

  end = file_bin.len - padding #Id do final do arquivo

  #print(end)
  
  count = 0

  #numero = 0

  #Dicionario com o codigo como chave e o símbolo como valor
  inv_dict_code = {_code: symbol for symbol, _code in code.items()}

  while count < end:
    values, count = mh.decoder_two(file_bin, count, inv_dict_code, tree, end)

    index = int.from_bytes(values[0],byteorder='big')
    size = int.from_bytes(values[1],byteorder='big')

    next_s = file_bin[count:count + 8].tobytes()
    count += 8

    if index > 0:
      index = len(search_buffer) - index

      for i in range(size):
        search_buffer.append(search_buffer[index + i])
        f_write.write(search_buffer[index + i])

    search_buffer.append(next_s)
    f_write.write(next_s)
    #numero += size + 1
    #print("Next: {}, search_buffer: {}, values: {}, numero: {}, index: {}".format(next_s, search_buffer, values, numero, index))

    if len(search_buffer) >= search_buffer_max:
        search_buffer = search_buffer[len(search_buffer) - search_buffer_max:]
  
  end = time.time()
  print('Demorou: {} segundos'.format(end - start))

  #print(search_buffer)

#----------------------------------------
def check_header(header):

  if header[:-4] == bs.Bits(hex= '0xf'):
    return header[4:].uint

  else: raise WrongHeader

class WrongHeader(Exception):
  pass

#---------------------------------------------------------------------------------------------
#Extrai os símbolos presentes
def get_symbols(_list):

  int_little = list(_list.findall('0b1')) #inteiros dos símbolos lidos na byteordem 'litte'

  symbols = [(255-s).to_bytes(1, byteorder= 'big') for s in int_little] #símbolos presentes em bytes

  return symbols

#--------------------------------------------------------------------------------------------
#Cria um array de inteiros com os tamanhos existentes
def get_lengths(bits_lengths):

  lengths = []

  for b in bits_lengths.tobytes():
    lengths.append(b)

  return lengths

if __name__ == "__main__":
  main()