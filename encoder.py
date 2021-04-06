import sys
import re
import time
#import numpy as np
#from matplotlib import pyplot as plt
import bitstring as bs
import my_huffman as mh

def main():

  header = bs.Bits(hex='0xF0') #Header sendo F + numero de bits de padding no final do arquivo
  
  filename = input("Informe o nome (caminho) do arquivo a ser comprimido: ")
  directory = input("Informe o nome do diretório do resultado (será o atual caso não informado): ")

  no_path_name = remove_path(filename)
  filename_result = add_path_bin(directory, no_path_name)

  try:
    with open(filename, 'rb') as f_read:
      with open(filename_result, 'wb') as f_write:
        print('Codificando... (pode demorar)')
        start = time.time()
        prob = write_or_getprob(f_read, f_write, writing= False)
        code, symbols_being, lengths = mh.encoder(prob) #Gera uma codificação de huffman

        f_write.write(header.tobytes()) #Escreve o header no arquivo (0xF0), poderiormente 0 será o tamanho do padding final
        f_write.write(symbols_being.tobytes()) #Escreve a sequência de existência dos símbolos (Huffman)
        f_write.write(lengths) #Escreve os tamanhos dos códigos na ordem lexicográfica de seus símbolos (Huffman)

        f_read.seek(0)
        padding = write_or_getprob(f_read, f_write, writing= True, code= code) #Escreve o artigo utilizando o LZ77 e o Huffman para as posições e tamanhos

        f_write.seek(0)
        f_write.write((header[:4] + padding).tobytes()) #Insere a quantidade final de padding no cabeçalho

        end = time.time()
        print('Demorou: {} segundos'.format(end - start))

  except IOError as ioe:
    sys.exit('Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  print("Terminado! Criado arquivo '{}'.\n".format(filename_result))

#--------------------------------------

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_bin(directory, no_path_name):
  bin_name = no_path_name + '.bin'
  return directory + '/' + bin_name if directory else bin_name

#Recebe os arquivos para leitura e escrita, e define se vai escrever no arquivo de escrita utilizando um code (dicionário de códigos) específico ou se gerará as probabilidades dos números resultantes
#Retorna o padding caso writing = True e um dicionário com as probabilidades caso False
def write_or_getprob (f_read, f_write, writing=True, code=None):
  #hist = []
  padding = 0

  if len(sys.argv) > 1:
    search_buffer_max = min(int(sys.argv[1]),255)
  else:
    search_buffer_max = 16
  search_buffer = []

  if len(sys.argv) > 2:
    look_ahead_buffer_max = min(int(sys.argv[2]), 255)
  else:
    look_ahead_buffer_max = 7
  look_ahead_buffer = []

  f_bytes = f_read.read(look_ahead_buffer_max)
  look_ahead_buffer = list(f_bytes)
  write_buffer = bs.Bits(bin='0b')

  symbols = {} #Dicionario com os simbolos e probabilidades

  n_triples = 0 #Contador dos numeros no arquivo

  while(f_bytes or len(look_ahead_buffer) > 0):

    triple = find_pattern(search_buffer, look_ahead_buffer)
    n_triples += 1
    
    next_s = triple[1] + 1
    f_bytes = f_read.read(next_s)

    if len(search_buffer) + next_s <= search_buffer_max:
      search_buffer = search_buffer + look_ahead_buffer[:next_s]

    else: 
      #Esperasse que com o tempo seja diff = next_s
      diff = len(search_buffer) - search_buffer_max + next_s #Diff maior que zero devido à condição do if
      search_buffer = search_buffer[diff:] + look_ahead_buffer[:next_s]

    look_ahead_buffer = look_ahead_buffer[next_s:] + list(f_bytes)

    if writing:

      index = triple[0].to_bytes(1, byteorder= 'big')
      size = triple[1].to_bytes(1, byteorder= 'big')

      if code:
        index = code[index]
        size = code[size]

      write_buffer += index + size + bs.Bits(bytes=triple[2])

      if write_buffer.len % 8 == 0: #A cada múltiplo de 8 bits de código gerado, escreve no arquivo e esvazia o buffer
        write_buffer.tofile(f_write)
        write_buffer = bs.Bits(bin='0b')

    else:
      for number in triple[:-1]:
        byte = number.to_bytes(1, byteorder= 'big')
        if byte in symbols.keys():
          symbols[byte] += 1
        else: symbols[byte] = 1


    #hist.append(triple[0])
    #hist.append(triple[1])

  if writing: 
    write_buffer.tofile(f_write) #Coloca o resto do código gerado no arquivo
    #Retorna o padding utilizado na última adição ao arquivo
    if write_buffer.len % 8 == 0:
      padding = 0
    else: padding = 8 - (write_buffer.len % 8)
    
    print(padding)
    return padding


  else:
    return {key: value/(n_triples*2) for key, value in symbols.items()} #Dividindo todos os valores pelo total
  #plt.hist(np.array(hist))
  #plt.title("Histogram")
  #plt.show()
  


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