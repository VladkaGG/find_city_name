""" Подсчет ошибочных названий городов, которые придется переименовывать вручную. """

langs = ['de', 'es', 'fr', 'it', 'nl', 'pl', 'pt', 'ro', 'tr']
count = 0
for lang in langs:
    with open('{}/errors.txt'.format(lang), 'r') as f:
        count += len(f.readlines())
print(count)
