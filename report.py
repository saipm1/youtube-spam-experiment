# This Python file uses the following encoding: utf-8

import os
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    f1_score,
    matthews_corrcoef,
    roc_auc_score,
    roc_curve
)


def calculate_scores(y_true, y_pred):

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # Ensure that the lists are both the same length
    assert(len(y_true) == len(y_pred))

    scores = {}
    scores['tp'] = sum((y_true == y_pred) & (y_true == 1))
    scores['tn'] = sum((y_true == y_pred) & (y_true == 0))
    scores['fp'] = sum((y_true != y_pred) & (y_true == 0))
    scores['fn'] = sum((y_true != y_pred) & (y_true == 1))

    scores['p'] = sum(y_true == 1)
    scores['n'] = sum(y_true == 0)

    scores['acc'] = accuracy_score(y_true, y_pred)
    scores['f1'] = f1_score(y_true, y_pred)
    scores['mcc'] = matthews_corrcoef(y_true, y_pred)
    scores['kappa'] = cohen_kappa_score(y_true, y_pred)

    try:
        scores['sc'] = float(scores['tp']) / (scores['tp'] + scores['fn'])
    except ZeroDivisionError:
        scores['sc'] = 0

    try:
        scores['bh'] = float(scores['fp']) / (scores['fp'] + scores['tn'])
    except ZeroDivisionError:
        scores['bh'] = 0

    # Compute ROC curve and ROC area
    # TODO roc_curve doesn't accept y_pred, but y_proba
    # scores['fpr'], scores['tpr'], _ = roc_curve(y_true, y_pred)
    # scores['roc_oneless_auc'] = 1 - roc_auc_score(y_true, y_pred)

    return scores


def csv_report(path, video_title, scores_list):

    filename = os.path.join(path, video_title + '.csv')
    with open(filename, 'w') as f:
        header = ['Classifier', 'Accuracy', 'Spam Caught (%)', 'Blocked Ham (%)',
                  'F-measure', 'MCC', 'Kappa', 'P', 'N', 'TP', 'TN', 'FP', 'FN']
        csv.writer(f).writerow(header)

        for classifier, score in scores_list:
            row = [classifier, score['acc'], score['sc'], score['bh'],
                   score['f1'], score['mcc'], score['kappa'],
                   score['p'], score['n'],
                   score['tp'], score['tn'], score['fp'], score['fn']]
            csv.writer(f).writerow(row)


def tex_report(filename, video_title, scores_list):
    caption = 'Resultados dos métodos de aprendizado de máquina para o ' \
              'vídeo{0}.'.format(video_title)
    label = 'tab:{0}'.format(video_title)

    s = '\\begin{table}[!htb]\n'
    s += '\\centering\n'
    s += '\\caption{{{0}}}\n'.format(caption)
    s += '\\label{{{0}}}\n'.format(label)
    s += '\\begin{tabular}{r|c|c|c|c|c|c|c|c|c|c}\n'
    s += '\\hline\\hline\n'
    s += 'Classifier & Acc (\\%) & SC (\\%) & BH (\\%) & '
    s += 'F-medida & MCC & Kappa '
    s += '& TP & TN & FP & FN '
    s += '\\\\ \\hline\n'

    for clf_title, sc in scores_list:
        s += '{0} & '.format(clf_title.replace('&', '\&'))
        s += '{0:.2f} & '.format(sc['acc'] * 100)
        s += '{0:.2f} & '.format(sc['sc'] * 100)
        s += '{0:.2f} & '.format(sc['bh'] * 100)
        s += '{0:.3f} & '.format(sc['f1'])
        s += '{0:.3f} & '.format(sc['mcc'])
        s += '{0:.3f} & '.format(sc['kappa'])
        s += '{0} & {1} & '.format(sc['tp'], sc['tn'])
        s += '{0} & {1} '.format(sc['fp'], sc['fn'])
        s += '\\\\ \n'

    s += '\\hline\\hline\n\\end{tabular}\n\\end{table}\n'

    with open(filename, 'w') as output_file:
        output_file.write(s)


def plot_bars(figurename, video_title, scores_list, metric):
    plt.figure()
    plt.title(video_title)
    plt.xlabel(metric.upper())

    performance = [scores[metric] for clf_title, scores in scores_list]
    classifiers = tuple(clf_title for clf_title, scores in scores_list)
    y_pos = np.arange(len(classifiers))
    plt.yticks(y_pos, classifiers)

    bar = plt.barh(y_pos, performance, align='center', alpha=0.4)
    best = performance[0]
    for i, p in enumerate(performance):
        if p == best:
            bar[i].set_color('r')

    plt.xticks(np.arange(0, 1.1, 0.1))  # guarantee an interval [0,1]
    plt.savefig(figurename + '_mcc.png', bbox_inches='tight')
    plt.savefig(figurename + '_mcc.pdf', bbox_inches='tight')
    plt.close()


def plot_roc(figurename, video_title, scores_list):
    plt.figure()
    plt.title(video_title)
    for clf_title, scores in scores_list:
        plt.plot(
            scores['fpr'], scores['tpr'],
            label=clf_title + ' (1 - AUC = %0.2f)' % scores['roc_oneless_auc'])

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")

    plt.savefig(figurename + '_roc.png', bbox_inches='tight')
    plt.savefig(figurename + '_roc.pdf', bbox_inches='tight')
    plt.close()
