rnc.data\_process.get\_fft
==========================

.. currentmodule:: rnc.data_process

.. autofunction:: get_fft

Resumo
------

Calcula espectro de frequencia para uma ``Trace`` usando janelas deslizantes,
remocao de tendencia, taper e FFT.

Parametros
----------

- ``trace``: ``obspy.Trace`` com serie temporal do sinal.
- ``WINDOW_LENGTH``: tamanho da janela (segundos).
- ``OVERLAP``: fracao de sobreposicao entre janelas.
- ``nb_pts``: parametro legado; o valor efetivo e recalculado pela funcao.

Retorno
-------

Tupla ``(result, freqs)``:

- ``result``: amplitudes normalizadas e achatadas.
- ``freqs``: vetor de frequencias correspondente (sem componente DC).

