@rem Patch Project Gutenberg's "A Study in Scarlet" ( http://www.gutenberg.org/files/244/244-0.txt )
@rem to remove front and end matter, including transcriber's footnotes.
@rem I used ssed.exe (from http://sed.sourceforge.net/grabbag/ssed/sed-3.62.zip ; see http://sed.sourceforge.net/grabbag/ssed/ )
@rem renamed to sed.exe. This creates a file with CR/LF line endings.
@rem If you use instead the one from Git for Windows, it creates a file with only LF (Unix-style) line endings.
sed -f 244-0.patch 244-0.txt > A_Study_in_Scarlet.txt
