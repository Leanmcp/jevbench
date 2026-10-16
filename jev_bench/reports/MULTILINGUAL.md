# Decision models in other languages (state and question translated)

Accuracy (%) over 5 slices, each weighted equally. In brackets: change from
English in points, then its paired bootstrap 95% interval.
Each model is scored on the cases that its English run and all its translated runs answered.

model                 cases  English  Chinese                     Arabic                      Hindi                         Vietnamese                
--------------------  -----  -------  --------------------------  --------------------------  ----------------------------  --------------------------
Clef                  1949   86.7     87.6 (+0.9, -0.3 to +2.2)   86.1 (-0.6, -1.9 to +0.8)   85.3 (-1.3, -3.0 to +0.2)     83.5 (-3.2, -4.7 to -1.7) 
pplx-decider v1.1     1949   84.3     82.4 (-1.9, -2.9 to -0.9)   82.6 (-1.7, -2.8 to -0.5)   79.7 (-4.6, -6.0 to -3.4)     81.8 (-2.5, -3.5 to -1.5) 
Microsoft Decision 1  1949   84.2     84.7 (+0.5, -1.1 to +2.1)   82.7 (-1.5, -3.1 to +0.1)   82.0 (-2.2, -3.9 to -0.4)     85.9 (+1.7, +0.3 to +3.1) 
Mercury Decide        1947   81.6     81.3 (-0.3, -1.7 to +1.1)   80.3 (-1.2, -2.8 to +0.3)   79.5 (-2.0, -3.6 to -0.5)     81.1 (-0.5, -2.1 to +1.0) 
Solar Decide          1949   79.5     75.2 (-4.3, -6.3 to -2.3)   72.7 (-6.8, -8.8 to -4.7)   72.9 (-6.6, -8.5 to -4.7)     70.4 (-9.1, -11.3 to -6.8)
Clef-omni             1949   79.2     79.4 (+0.1, -1.5 to +2.0)   78.6 (-0.6, -2.2 to +1.0)   75.6 (-3.6, -5.4 to -1.9)     78.7 (-0.5, -2.3 to +1.2) 
GPT-6 Luna Decisions  1947   79.2     78.6 (-0.6, -2.1 to +0.9)   80.3 (+1.1, -0.1 to +2.4)   78.0 (-1.2, -2.6 to +0.3)     79.7 (+0.5, -0.9 to +1.9) 
ScaleDown Classify-1  1949   78.8     70.4 (-8.4, -10.6 to -6.2)  72.1 (-6.7, -8.7 to -4.7)   76.2 (-2.6, -4.6 to -0.6)     71.2 (-7.6, -10.0 to -5.3)
Clef-flash            1949   78.4     78.7 (+0.2, -1.1 to +1.8)   78.2 (-0.3, -1.5 to +1.0)   78.8 (+0.4, -1.4 to +2.2)     81.7 (+3.3, +1.9 to +4.8) 
Span-01               1949   76.4     82.2 (+5.8, +4.1 to +7.6)   76.7 (+0.3, -1.5 to +1.9)   63.7 (-12.7, -14.9 to -10.4)  75.3 (-1.1, -2.6 to +0.4) 
Drex v1.5             1946   75.3     75.9 (+0.6, -0.7 to +2.1)   74.4 (-0.9, -2.2 to +0.5)   72.9 (-2.4, -4.0 to -0.7)     77.2 (+1.9, +0.5 to +3.4) 
Solar Decide Flash    1949   74.7     70.6 (-4.1, -6.2 to -1.9)   65.1 (-9.6, -11.9 to -7.0)  68.8 (-5.9, -8.1 to -3.5)     69.9 (-4.8, -7.0 to -2.5) 
Kev 4B                1949   73.3     71.3 (-2.0, -3.5 to -0.5)   71.0 (-2.2, -4.0 to -0.4)   66.8 (-6.5, -8.2 to -4.8)     71.7 (-1.5, -3.0 to -0.0) 
TEv1 4B (exp.)        1943   69.2     73.8 (+4.6, +3.1 to +6.2)   73.8 (+4.7, +2.9 to +6.6)   68.3 (-0.9, -2.4 to +0.7)     72.1 (+2.9, +1.0 to +4.7) 
mean over models             78.6     78.0 (-0.6)                 76.8 (-1.9)                 74.9 (-3.7)                   77.2 (-1.5)               

## By slice (mean over models)

slice                     English  Chinese  Arabic  Hindi  Vietnamese
------------------------  -------  -------  ------  -----  ----------
jailbreak_classification  94.8     93.0     89.7    92.1   92.9      
prompt_injections         71.8     72.5     72.5    70.0   71.8      
aegis2                    81.1     80.8     78.8    73.8   78.9      
aegis2_response           76.1     75.6     76.8    75.1   76.0      
atbench500                69.3     68.1     65.9    63.5   66.2      

## Coverage

model                 language    answered  paired
--------------------  ----------  --------  ------
Clef                  Chinese     1979      1949  
Clef                  Arabic      2007      1949  
Clef                  Hindi       1999      1949  
Clef                  Vietnamese  1968      1949  
Clef-flash            Chinese     1979      1949  
Clef-flash            Arabic      2007      1949  
Clef-flash            Hindi       1999      1949  
Clef-flash            Vietnamese  1968      1949  
Clef-omni             Chinese     1979      1949  
Clef-omni             Arabic      2007      1949  
Clef-omni             Hindi       1999      1949  
Clef-omni             Vietnamese  1968      1949  
pplx-decider v1.1     Chinese     1979      1949  
pplx-decider v1.1     Arabic      2007      1949  
pplx-decider v1.1     Hindi       1999      1949  
pplx-decider v1.1     Vietnamese  1968      1949  
GPT-6 Luna Decisions  Chinese     1979      1947  
GPT-6 Luna Decisions  Arabic      2006      1947  
GPT-6 Luna Decisions  Hindi       1998      1947  
GPT-6 Luna Decisions  Vietnamese  1968      1947  
Microsoft Decision 1  Chinese     1979      1949  
Microsoft Decision 1  Arabic      2007      1949  
Microsoft Decision 1  Hindi       1999      1949  
Microsoft Decision 1  Vietnamese  1968      1949  
Solar Decide          Chinese     1979      1949  
Solar Decide          Arabic      2007      1949  
Solar Decide          Hindi       1999      1949  
Solar Decide          Vietnamese  1968      1949  
Solar Decide Flash    Chinese     1979      1949  
Solar Decide Flash    Arabic      2007      1949  
Solar Decide Flash    Hindi       1999      1949  
Solar Decide Flash    Vietnamese  1968      1949  
Drex v1.5             Chinese     1977      1946  
Drex v1.5             Arabic      2007      1946  
Drex v1.5             Hindi       1998      1946  
Drex v1.5             Vietnamese  1968      1946  
Mercury Decide        Chinese     1979      1947  
Mercury Decide        Arabic      2007      1947  
Mercury Decide        Hindi       1999      1947  
Mercury Decide        Vietnamese  1966      1947  
TEv1 4B (exp.)        Chinese     1974      1943  
TEv1 4B (exp.)        Arabic      2005      1943  
TEv1 4B (exp.)        Hindi       1998      1943  
TEv1 4B (exp.)        Vietnamese  1965      1943  
Kev 4B                Chinese     1979      1949  
Kev 4B                Arabic      2007      1949  
Kev 4B                Hindi       1999      1949  
Kev 4B                Vietnamese  1968      1949  
ScaleDown Classify-1  Chinese     1979      1949  
ScaleDown Classify-1  Arabic      2007      1949  
ScaleDown Classify-1  Hindi       1999      1949  
ScaleDown Classify-1  Vietnamese  1968      1949  
Span-01               Chinese     1979      1949  
Span-01               Arabic      2007      1949  
Span-01               Hindi       1999      1949  
Span-01               Vietnamese  1968      1949  
