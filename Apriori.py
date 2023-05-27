import pandas as pd
import re
import time

support = 0.005  # 频繁项集的最小支持度设为0.005
confidence = 0.5  # 关联规则的置信度为0.5


def generateC1(dataset):
    C1 = set()
    for data in dataset:
        for item in data:
            itemset = frozenset([item])
            C1.add(itemset)
    return C1


def isapriori(ckitem, lx):
    for item in ckitem:
        ck_sub = ckitem - frozenset([item])
        if ck_sub not in lx:
            return False
    return True


def generateCk(lx, k):
    """
    lx:Lk-1,存储着所有的频繁k-1项集
    """
    Ck = set()
    length = len(lx)
    listlx = list(lx)
    for i in range(length):
        for j in range(i, length):
            l1 = list(listlx[i])
            l2 = list(listlx[j])
            l1.sort()
            l2.sort()
            if l1[0:k - 2] == l2[0:k - 2]:
                ckitem = listlx[i] | listlx[j]  # 连接
                if isapriori(ckitem, lx):
                    Ck.add(ckitem)
    return Ck


def PCY(lx, k, bucket_num=2000):
    hash_table = {}
    bucketcount = [0 for x in range(0, bucket_num)]
    bitmap = [0 for x in range(0, bucket_num)]
    # PCY pass 1
    pair = set()
    Ck = set()
    length = len(lx)
    listlx = list(lx)
    for i in range(length):
        for j in range(i, length):
            l1 = list(listlx[i])
            l2 = list(listlx[j])
            l1.sort()
            l2.sort()
            if l1[0:k - 2] == l2[0:k - 2]:
                ckitem = listlx[i] | listlx[j]  # 连接
                if isapriori(ckitem, lx):
                    hash_table[ckitem] = (i * j) % bucket_num
                    #print(hash_table[ckitem])
                    bucketcount[hash_table[ckitem]] += 1
                    pair.add(ckitem)
                    # between pass
    for i in range(0, len(bucketcount)):

        if bucketcount[i] > 0.005 * len(lx):
            bitmap[i] = 1
        else:
            bitmap[i] = 0
    # print('bitmap为：')
    # for x in bitmap:
    #     print(x, end="")
    # print('\n')
    for item in pair:
        if bitmap[hash_table[item]] == 1:
            Ck.add(item)
    return Ck


def generateLk(dataset, Ck, min_support, support_data):
    item_num = {}
    Lk = set()
    for data in dataset:
        for item in Ck:
            if item.issubset(data):
                if item not in item_num:
                    item_num[item] = 1
                else:
                    item_num[item] += 1
    sum_lk = float(len(dataset))
    for item in item_num:
        if (item_num[item] / sum_lk) >= min_support:
            Lk.add(item)
            support_data[item] = item_num[item] / sum_lk
    return Lk


def fre_items(dataset, k, min_support):
    support_data = {}  # 字典，key值为频繁项集，value为对应支持度
    L = []
    C1 = generateC1(dataset)
    L1 = generateLk(dataset, C1, min_support, support_data)
    Lx = L1.copy()
    L.append(Lx)
    C2 = PCY(Lx, 2)
    # PCY pass 2
    L2 = generateLk(dataset, C2, min_support, support_data)
    Lx = L2.copy()
    L.append(Lx)

    #for i in range(3, k + 1):
    i = 3
    while 1:
        Ci = generateCk(Lx, i)
        Li = generateLk(dataset, Ci, min_support, support_data)
        if len(Li)==0:
            break
        Lx = Li.copy()
        L.append(Lx)
        i += 1
    return L, support_data


def generate_big_rules(L, support_data, min_conf):
    big_rule_list = []
    sub_set_list = []
    for i in range(0, len(L)):
        for freq_set in L[i]:
            for sub_set in sub_set_list:
                if sub_set.issubset(freq_set):
                    conf = support_data[freq_set] / support_data[freq_set - sub_set]
                    lift = conf / support_data[sub_set]
                    big_rule = (freq_set - sub_set, sub_set, conf, lift)
                    if conf >= min_conf and big_rule not in big_rule_list:
                        # print freq_set-sub_set, " => ", sub_set, "conf: ", conf
                        big_rule_list.append(big_rule)
            sub_set_list.append(freq_set)
    return big_rule_list

#def generate_Lift(L, rule_list, support_data):

#if __name__ == '__main__':
dataset = []
with open("data.txt") as file:
  for line in file:
      a = []
      for el in line.replace("[","").replace("]","").split(","):
          a.append(int(el))
      dataset.append(a)
start = time.time()
L, support_data = fre_items(dataset, k=4, min_support=0.005)
big_rules_list = generate_big_rules(L, support_data, min_conf=0.5)
end = time.time()
for Lk in L:
    print("=========================================================")
    print("frequent " + str(len(list(Lk)[0])) + "-itemsets\t\tsupport")
    print("=========================================================")
    for freq_set in Lk:
        print(freq_set, support_data[freq_set])
print("Big Rules")
for item in big_rules_list:
    print(item[0], "=>", item[1], "conf: ", item[2],"lift：",item[3])
i = 1
for Lk in L:
    print("频繁", i, "项数为：", len(Lk))
    i = i + 1
print('规则数为:', len(big_rules_list))
sum = 0
for item in big_rules_list:
    if (item[2]>0.8 and item[3]>10.0):
        sum += 1
        print(item[0], "=>", item[1], "conf: ", item[2], "lift：", item[3])
print(sum)
print('程序运行时间为', end - start, 's')