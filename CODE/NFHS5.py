import fitz
import pandas as pd
import re 
import pickle
import progressbar
  

class write2df:
    
    def __init__(self):
        with open('../DATA/states.pickle', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.states = pickle.load(f)

        with open('../DATA/districts.pickle', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.districts = pickle.load(f)

        with open('../DATA/indicators.pickle', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.indicators = pickle.load(f)

        self.ind = self.indicators[0] + self.indicators[1] + self.indicators[2]
        

    def getstats(self, statename, d):
        #print(state, ', ', d, ':')
        try: 
            doc  = fitz.open('../DATA/NFHS5/' + self.states[statename] + '_' + d + '.pdf') 
        except: 
            print(self.states[statename]+'_'+d+'.pdf : No such file found\n')
            return []
        else:  
            # STEP 1: READ PAGE USING 'fitz' AND REMOVE ALL '\n' AND WHITESPACES
            # PAGE 3:
            page1 = doc.load_page(2)
            text1 = page1.get_text('text')
            t1    = text1.replace('\n', '')
            para1 = t1.replace(' ', '')

            # PAGE 4:
            page2 = doc.load_page(3)
            text2 = page2.get_text('text')
            t2    = text2.replace('\n', '')
            para2 = t2.replace(' ', '')

            # PAGE 5:
            if statename == 'West_Bengal' and d == 'Jalpaiguri':
                page3 = doc.load_page(5)
            else:
                page3 = doc.load_page(4)
            text3 = page3.get_text('text')
            t3    = text3.replace('\n', '')
            para3 = t3.replace(' ', '')

            doc.close()
            para = para1 + para2 + para3

            # STEP 2: CORRECTIONS 
            if (d == 'Wardha' and statename == 'Maharashtra') or (d == 'Mahisagar' and statename == 'Gujarat'):
                for i in range(9, 31):
                    rightside = self.ind[i].split('.')[1]
                    leftside  = self.ind[i].split('.')[0]
                    if i == 11:
                        rightside = 'Householdswithanyusualmembercoveredbyahealthschemeorhealthinsurance(%)'
                    idot = para.find(rightside) 
                    para = para[:idot-len(leftside)-1]+self.ind[i]+para[idot+len(rightside):]
            if statename == 'Puducherry':
                phrase = 'HypertensionamongAdults(age15yearsandabove)Womenna92.Mildlyelevatedbloodpressure(Systolic140-159mmofHgand/orDiastolic90-99mmofHg)(%)'
                para   = para.replace(phrase, self.ind[len(self.indicators[0])+len(self.indicators[1])+25])
            if (d == 'Raigarh' and statename == 'Maharashtra'):
                phrase = 'TobaccoUseandAlcoholConsumptionamongAdults(age15yearsandabove)na101.Womenage15yearsandabovewhouseanykindoftobacco(%)'
                para    = para.replace(phrase, self.ind[len(self.indicators[0])+len(self.indicators[1])+34])
                phrase = 'na102.Menage15yearsandabovewhouseanykindoftobacco(%)'
                para    = para.replace(phrase, self.ind[len(self.indicators[0])+len(self.indicators[1])+35])

            # STEP 3: Read numerical data in string form
            previndx = 0
            begin_indx = []
            for indic in self.ind:
                previndx = para.find(indic)
                begin_indx.append(previndx)
            if -1 in begin_indx:
                print(statename, d, ':', begin_indx, ' : ', len(begin_indx), '\n')
                print(para2)
            end_indx = [begin_indx[i]+len(self.ind[i]) for i in range(0,len(begin_indx))]
            stats = []
            for i in range(0,len(self.ind)-1):
                stats.append(para[end_indx[i]:begin_indx[i+1]])
            del stats[len(self.indicators[0] + self.indicators[1])-1]
            del stats[len(self.indicators[0])-1]

            return stats, 'NFHS-4(2015-16)' in para
        
        
    def writeStatsToDF(self, stats, isNFHS4):
        # Error codes  ->   0: None, 
        #                   1: based on 25-49 unweighted data points, 
        #                   2: not available, 
        #                   3: not shown, based on < 25 data points
        #                   4: no comparable estimates are available from NFHS-4 in this 
        #                      district due to district boundary changes or a newly formed district.         
        err_NFHS4 = []
        err_NFHS5 = []
        stats_NFHS4 = []
        stats_NFHS5 = []    
        if isNFHS4: # both NFHS-4 and NFHS-5 data available
            for i in range(0,len(stats)): 
                s = stats[i]
                errcode = [0, 0]
                if s[0] == '(':
                    errcode[0] = 1
                    m = s.find(')')-2
                    s = ''.join(re.split('[\(\)]', s))
                if s[len(s)-1] == ')':
                    errcode[1] = 1
                    m = s.find('(')-1
                    s = ''.join(re.split('[\(\)]', s))
                if s[0] == 'n':
                    errcode[0] = 2
                    m = s.find('a')
                if s[len(s)-1] == 'a':
                    errcode[1] = 2
                    m = len(s)-3
                if s[0] == '*':
                    errcode[0] = 3
                    m = 0
                if s[len(s)-1] == '*':
                    errcode[1] = 3
                    m = len(s)-2
                err_NFHS5.append(errcode[0])
                err_NFHS4.append(errcode[1])
                if errcode == [0, 0]:
                    if i not in [2,3,38]:
                        m = s.find('.')+1
                    else:
                        m = s.find(',')
                        if m == 1 or m == 2:
                            # comma in second position from left
                            m = m + 3
                        elif m == len(s) - 1 - 3:
                            # comma in 4th position from right
                            m = m - 2
                        else:
                            # no comma found, so 999 or less on each column
                            m = 2
                if m > -1:
                    #stats_num.append([s[:m+1], s[m+1:]])
                    stats_NFHS5.append(s[:m+1]) 
                    stats_NFHS4.append(s[m+1:]) 
                else:
                    print(statename, d, ':', s, len(s))
            stats_NFHS4 = [re.sub('[,\(\)\*]', '', s) for s in stats_NFHS4]
            stats_NFHS4 = [re.sub('na', '', s) for s in stats_NFHS4]
            stats_NFHS5 = [re.sub('[,\(\)\*]', '', s) for s in stats_NFHS5]
            stats_NFHS5 = [re.sub('na', '', s) for s in stats_NFHS5]
        else:   # only NFHS-5 data available
            for s in stats:
                errcode = [0, 4]
                if s[0] == '(':
                    errcode[0] = 1
                if s[0] == 'n':
                    errcode[0] = 2
                if s[0] == '*':
                    errcode[0] = 3
                #err_code.append(errcode)
                err_NFHS5.append(errcode[0])
                err_NFHS4.append(errcode[1])
                stats_NFHS5.append(s)
                #stats_NFHS5.append(''.join(re.split('[na\(\)\*,]', s)))
            stats_NFHS5 = [re.sub('[,\(\)\*]', '', s) for s in stats_NFHS5]
            stats_NFHS5 = [re.sub('na', '', s) for s in stats_NFHS5]
            stats_NFHS4 = ['' for s in stats_NFHS5]    

        return stats_NFHS4, stats_NFHS5, err_NFHS4, err_NFHS5

    
if __name__ == '__main__':
    widgets = [' [',
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
         '] ',
           progressbar.Bar('*'),' (',
           progressbar.ETA(), ') ',
          ]
  
    bar = progressbar.ProgressBar(max_value=704,
                              widgets=widgets).start()


    NFHS5 = write2df()
    
    str_nfhs5 = ['Q'+str(i)+'_NFHS5' for i in range(1, len(NFHS5.ind)-2)]
    str_nfhs4 = ['Q'+str(i)+'_NFHS4' for i in range(1, len(NFHS5.ind)-2)]
    err_nfhs5 = ['err'+str(i)+'_NFHS5' for i in range(1, len(NFHS5.ind)-2)]
    err_nfhs4 = ['err'+str(i)+'_NFHS4' for i in range(1, len(NFHS5.ind)-2)]
    cols      = ['State', 'District']+str_nfhs5+str_nfhs4+err_nfhs5+err_nfhs4
    df = pd.DataFrame(columns = cols)

    i = 0
    for state in NFHS5.states:
        for d in NFHS5.districts[state]:
            stats, isNFHS4 = NFHS5.getstats(state, d)
            stats_NFHS4, stats_NFHS5, err_NFHS4, err_NFHS5 = NFHS5.writeStatsToDF(stats, isNFHS4)
            df.loc[len(df.index)] = [state, d] + stats_NFHS5 + stats_NFHS4 + err_NFHS5 + err_NFHS4
            bar.update(i)
            i += 1
            
            
    df.to_csv('NFHS5.csv')
