import csv

def saveAsCsv(result, league_str, dataframe, filename):
    with open('{}_{}.csv'.format(filename, league_str), "w") as output:  # 크롤링한 결과물들을 csv파일의 형태로 저장
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(dataframe)
        for index, val in enumerate(result):
            try:
                writer.writerow(val)
            except Exception as e:
                print('index: ', index)
                print(e)