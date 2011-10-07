****************
Citing *edittag*
****************

.. [Faircloth:2011] Faircloth BC, Glenn TC:  Large sets of edit metric sequence tags to enable horizontal scaling of reads from massively parallel sequencing.  Nature Precedings 2011. doi:  xxxx.yy.zz

Abstract
========

Massively parallel DNA sequencing technologies provide exponential increases in the amount of data returned from the sequencing process, relative to traditional (Sanger-based) techniques. Tracking groups of reads in solution using synthetic oligonucleotide tags (sequence tags) enables the distribution of these data across many samples. Because of sequencing error, sequence tags should be drawn from an appropriate error-correcting code over the alphabet [A,C,G,T].  This method ensures that sequencing error does not cause tags to inappropriately cross-over while also enabling correction and recovery of incorrectly-sequenced tags. The set of available tags should be large, allowing sample multiplexing to scale with rapid changes in sequencing platform output.  Here, we provide several large sets of edit-metric sequence tags ranging from four to 10 nucleotides in length and edit distance three to nine.  We also provide several tools, written in Python, to facilitate the design of edit-metric-based sequence tags, check existing sets of sequence tags for conformance to the edit metric, and apply sequence tags to primers and/or adapters.