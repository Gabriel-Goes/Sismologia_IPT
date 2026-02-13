# Seismic Event Discriminator


Gabriel Goes Rocha de Lima <gabrielgoes@usp.br>
qua., 11 de fev., 14:30 (há 2 dias)
para Marcelo, Lucas

Boa tarde, Lucas e Bianchi, tudo bem com vocês?

Nestes últimos dois dias eu me dediquei a revisar meu código antigo e documentar o que eu havia feito utilizando sphynx e github pages. Consegui reproduzir todo o fluxo novamente fazendo testes documentados.

O que vou iniciar agora é o processo de reescrever o código do zero em uma nova branch vazia. vou arquivar todas as outras branches e criar uma nova main e uma chamada seismic-event-discriminator, onde farei as alterações de teste e vou executar merge na principal.

Em seisapp, eu deixarei os jupyter notebooks apresentando o código executado. Não importarei nenhuma biblioteca nem chamarei nenhum script bash dentro dos jupyter notebooks, todo o processo estará contido dentro do próprio, pois assim ficará mais fácil para que vocês possam verificar o que o código está fazendo, sem precisar abrir a documentação ou entrar no código fonte.

Mas mesmo assim, farei em paralelo um script bash que executa o processo desenvolvido em python de forma linear desde a aquisição dos dados até a análise e compilação de um PDF com LaTeX.

Se eu criar os jupyter notebooks dentro de 'gabrielgoes@seisapp:$HOME/' vocês tem acesso? Caso sim, farei isso a partir de hoje. Escrevendo o processo em .ipynb em minha home. Criarei um arquivo para cada uma das 5 etapas do fluxo:

 Construção de Catalog através de .csv adquirido via MOHO
 Seleção de sismos em região de grande atividade mineira de MG, <4mag & <10km
 Aquisição de formas de onda (60s)
 Alimentação da CNN (.mseed -> .npy)
 Análise dos resultados (plots de gráficos e mapas)
Talvez 1 e 2 possam estar no mesmo arquivo.

Agredeço pela oportunidade.

Respeitosamente,



--
Gabriel G. R. de Lima
Laboratório de Inteligência Artificial IGc/USP Intelli+Geo
image.png
Marcelo B. de Bianchi
qui., 12 de fev., 07:52 (há 1 dia)
para mim, Lucas

Ola Gabriel,

Eu consigo, o lucas provavelmente não. Mas o mais importante de você ter os notebooks é pela documentação.

Agora algumas dúvidas com relação aos pontos que voce trouxe:

Etapas 1 e 2)

Sim, as etapas 1 e 2 deveriam estar no mesmo processo que eu entendo ...

Uma dúvida sobre o passo 1, voce vai ler de um csv, mas as leituras em um csv é meio estranho, como vai ser isso? Consegue detalhar mais o que esta pensando?

ainda entendo que as etapas 1) e 2) leem um arquivo de catalogo, selecionam e quebram eles em diversos arquivos [xml|json] que comento abaixo

Esse processo poderia ser um notebook de seleção.

Etapa 3)

A etapa 3, eu faria de uma forma que ele acesse os dados e construa uma base local de análise, de forma que, se daqui seis meses você precisar adicionar outros eventos você pode fazer isso facilmente. Junto com cada arquivo de forma de onda eu guardaria os dados do evento, com os tempos de pick em cada estação. Esses arquivos paramétricos dos eventos, seriam gerados pela etapa 1,2 e poderiam ser extendidos nesta etapa 3, por exemplo pelo cálculo do SNR, para cada pick. I.e.

sismo_blah.[xml|json]
sismo_blah.ms

sismo_bleh.[xml|json]
sismo_bleh.ms

...

sismo_bluh.[xml|json]
sismo_bluh.ms

Sobre of formatos: O XML seria tipo QuakeML, se voce alimentar a sua etapa 1e2 de quakeml seria razoável aqui usar quakeml. Se voce usar outra coisa, talvez partiria para um json para ter mais flexibilidade.

Notebook ou script? Não sei dizer.

Etapa 4)

Aqui  eu faria uma forma de suportar paralel processing, já que voce tem N arquivos da etapa anterior e precisa rodar N vezes a CNN, isso e burramente paralelizável e pode trazer bastante ganho. Tem várias formas de fazer isso, a mais fácil com shell script usando um script que tenho chamado runp.sh + um script em python que voce faria para rodar um dado.

Esta etapa para mim deveria ser o ms+json -> gerar um out, com a saida da rede, outra alternativa é ele modificar o JSON colocando o resultado dentro do JSON (mais elegante, mas pode dar mais trabalho).

Etapa 5)

Isso é um ou mais notebooks.

Aguardo seus comentários,

abraços,  Bianchi
Gabriel Goes Rocha de Lima <gabrielgoes@usp.br>
qui., 12 de fev., 08:33 (há 1 dia)
para Marcelo

Bom dia, professores. Obrigado pelas ideias.

Respondendo a dúvida do professor Bianchi, quanto às etapas 1 e 2,

O arquivo 'csv' que me referi, é um arquivo de texto adquirido através do '/rq/event' ou '/fdsnws/event/1/builder'.

A ideia aqui, ainda na etapa de catálogo, era adquirir o catálogo disponibilizado na web ('txt'/'qml') e construir um objeto obspy (Catalog.events).

Agradeço novamente suas contribuições quanto aos passos seguintes. Vou começar a executar este plano.

abs, Gabriel
Marcelo B. de Bianchi
qui., 12 de fev., 08:44 (há 1 dia)
para mim

então o arquivo é quakeml e não csv.

bainchi
--
Centro de Sismologia
IAG / USP
T: +55 (11) 3091-4743 M: +55 (11) 9820-10-930
W: https://www.sismo.iag.usp.br/
Lucas Schirbel
qui., 12 de fev., 13:18 (há 1 dia)
para Marcelo, mim

Fala Gabriel,

Eu não tenho acesso à seisapp, mas tenho acesso ao seu github. Então essa parte está tranquila, desde que você mantenha os códigos sincronizados.
Sobre as etapas:

1) e 2) Acho que a gente tinha comentado que o catálogo final a ser lido para os sismos seria o catálogo do boletim brasileiro? Esse é o mesmo da MOHO? Me corrija se eu estiver errado. Talvez exista outra maneira de ler esse catálogo que não seja exportar do site para csv, como o Bianchi falou.

Não tenho comentários para as outras etapas além do que o Bianchi já disse. Ansioso para ver os resultados dessa nova região com os filtros aplicados!

Abraços,

Lucas
Marcelo B. de Bianchi
qui., 12 de fev., 15:29 (há 23 horas)
para Lucas, mim

Ola Lucas,

Eu não tenho acesso à seisapp, mas tenho acesso ao seu github. Então essa parte está tranquila, desde que você mantenha os códigos
1) e 2) Acho que a gente tinha comentado que o catálogo final a ser lido para os sismos seria o catálogo do boletim brasileiro? Esse é o mesmo da MOHO? Me corrija se eu estiver errado. Talvez exista outra maneira de ler esse catálogo que não seja exportar do site para csv, como o Bianchi falou.

Não é não. voce esta correto lucas, o boletim seria o ideal pois é + citável e validável.

Não tenho comentários para as outras etapas além do que o Bianchi já disse. Ansioso para ver os resultados dessa nova região com os filtros aplicados!

abraços, Bianchi



### Rascunho
Sim, nosso objetivo agora é usar o catálogo do boletim.Pelo que entendi do https://moho.iag.usp.br/eq/bulletin/ temos um boletim publicado em uma versão estática, em que foram realizadas correções para sismos antigos. O catálogo via FDSN é um produto dinâmico onde alterações e correções são feitas rotineiramente pelos técnicos do IAG.
Para deixar claro, o método antigo que eu fazia era entrar em moho.iag.br -> Dados -> Catálogo e baixar o arquivo no formato txt e salvando o .miniseed de acordo com a estrutura estabelecida pelo software da Celine Hourcade:
Sendo evento o DateTime:
mseeds/EVENTO/net_sta_EVENTO.MSEED.
Estabelecendo a nova estrutura, posso utilizar o catalogo estatico do boletim SISBRA (versao v2024May09) em ``catalogs/sisbra/catalogo_RAW.dat`` como fonte "estatica/citavel", e entao:
 1. Filtrar o RAW e gerar um catálogo derivado só com os eventos de interesse, por exemplo:
     catalogo_MG_mag<4.9_deep<10km.dat (e equivalente em CSV, se ajudar).
 2. Converter esse catálogo filtrado para um QuakeML (mínimo: origin + magnitude + informações básicas), e em seguida “quebrar” em 1 metadado por
     evento, do jeito que o Bianchi sugeriu (arquivo paramétrico por evento).
 3. Organizar em uma pasta por evento com tag temporal no estilo da Céline (DateTime), por exemplo:
     ./eventos/YYYYMMDDTHHMMSS/
     e dentro de cada pasta guardar os dois tipos de arquivo:

  3.1 event.xml/event.json (podemos adicionar SNR, output da CNN etc) Quakeml é possível fazer isto?
  3.2 os .mseed baixados (1 por estação/pick), mantendo uma convenção consistente de nomes.

  Faz sentido para vocês esta estrutura?
  - ``catalogs/sisbra/Makefile`` gera catalogos derivados (filtros) a partir do boletim
  - criamos um QuakeML
  - cria a árvore   -> ./data/YYYYMMDDTHHMMSS/                       -> event.xml ou event.json;                       -> NET_STA_DATETIME.miniseed (-10s p +50s)
O miniseed será adquirido através do obspy buscando pelo evento;
Boletim SísmicoO boletim sísmico publicado pelo Centro de Sismologia da USP é resultado da re-análise do catálogo de eventos do Centro e consiste em um conjunto de informação tabulada para coordenadas, hora de origem e magnitude dos terremotos ocorridos principalmente no Brasil que são detectados e analisados pelo Centro de Sismologia.Enquanto que o catálogo é um produto dinâmico, o boletim depois de criado é estático. Um evento, em um determinado boletim, não é mais atualizado. Quando existe uma atualização, é feita uma nova versão do boletim que é então disponibilizada. Acompanhando cada boletim é também disponibilizado um arquivo README que descreve em detalhes como a informação é disponibilizada.Versão AtualA versão atual do Boletim do Catálogo Brasileiro (SISBRA) é a v2024May09. Esta versão inclui eventos até 31 de dezembro de 2023 além de inúmeras correções compiladas para sismos mais antigos e mesmo de formatação do catálogo.Download:Arquivo ZIP contendo o catálogo em DAT, CSV e XLSX (Microsoft Excel)Mapa Atualizado (em PDF)Código fonte (em ZIP ou TAR.GZ)A partir desta versão o boletim é gerado a partir do SISBRA distribuído a partir do seu repositório GIT.Outras versõesAs versões anteriores do boletim estão disponíveis aqui. Se você está buscando informações mais recentes do que a disponível na nossa última atualização, você pode consultar os dados no nosso servidor fdsn, ou então, acessar o boletim preliminar mantido pelos analistas do Centro de Sismologia.ColaboraçãoDiferentes empresas e instituições contribuem com informação para a preparação do boletim, dentre elas:
