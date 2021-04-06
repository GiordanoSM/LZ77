# LZ77
## Informações
***Autor:** Giordano Süffert Monteiro

**Versão Python:** 3.7.1

**Executado pela linha de comando**

## Execução de encoder.py

### Argumentos

Possível passagem de parâmetro na hora de execução indicando o tamanho do search_buffer e do look_ahead_buffer, respectivamente; sendo o default 16 e 7 (bytes), equanto valor o máximo é de 255 (bytes), para ambos.

Será pedido o nome do arquivo a ser codificado. Incluir o caminho até ele a partir do diretório atual.

**Exemplo:**
  >python3 encoder.py 255

  >Informe o nome do arquivo a ser comprimido: arquivos/fonte0.txt
  >Informe o nome do diretório do resultado (será o atual caso não informado): bin255 

### Resultado

O arquivo resultante terá o mesmo nome do arquivo lido, e estará ou no mesmo diretório que ele, ou em outro caso tenha sido especificado na chamada do programa.

**Exemplo:** *bin255/fonte0.txt.bin*

## Execução de decoder.py

### Argumentos

Possível passagem de parâmetro na hora de execução indicando o tamanho do search_buffer, sendo o default 16 (bytes) e o máximo 255 (bytes).

Será pedido o nome do arquivo a ser decodificado. Incluir o caminho até ele a partir do diretório atual. É importante que para que o algoritmo funcione corretamente, o tamanho do buffer de busca utilizado na decodificação deve ser maior ou igual àquele utilizado na codificação.

**Exemplo:**

  >python3 decoder.py 255

  >Informe o nome do arquivo a ser descomprimido: bin255/fonte0.txt.bin
  >Informe o nome do diretório do resultado (será o atual caso não informado): results 

### Resultado

O arquivo resultante terá o mesmo nome do arquivo lido, retirando as últimas 4 letras (tirando o .bin) e estará ou no mesmo diretório que ele, ou em outro caso tenha sido especificado na chamada do programa.

**Exemplo:** *results/fonte0.txt*
