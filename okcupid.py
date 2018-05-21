# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:02:18 2018

@author: Sony
"""
from math import sqrt
import json

IMPORTANCE_POINTS = [0, 1, 10, 50, 250]

### Two short classes only defining objects and their attributes

class User:
    
    def __init__(self, iden, questions):
        self.iden = iden
        self.questions = questions
        #additional attribute : list of Id of questions that were answered by user
        self.answered_questions = [q.q_id for q in questions] 
        
    
class Question:
    
    def __init__(self, q_id, answer, exp_answer, importance) :
        self.q_id = q_id
        self.answer = answer
        self.exp_answer = exp_answer
        self.importance = importance
        

### The main class, containing the methods for matches computation
class Okcupid:
    
    def __init__(self, users) :
        self.users = users
    
    
    #a method to find the intersected set of common answered questions
    def find_S(self, userA, userB) :
        S = []
        #S is a list of indexes
        for a_q_id in userA.answered_questions :
            if a_q_id in userB.answered_questions : 
                S.append(a_q_id)
        return S
    
    def get_match_score(self, userA, userB) :
        #Initializations
        AsatisfiesB = [0, 0]
        BsatisfiesA = [0, 0]
        S = self.find_S(userA, userB)
        if len(S) == 0 : 
            print("no common question between %s and %s" % (userA.iden, userB.iden))
            return 0
        
        #The match computation
        for a_q_id in S :
            questionA = userA.questions[S.index(a_q_id)]
            questionB = userB.questions[S.index(a_q_id)]
            AsatisfiesB[0] += IMPORTANCE_POINTS[questionB.importance] * (questionA.answer in questionB.exp_answer)
            BsatisfiesA[0] += IMPORTANCE_POINTS[questionA.importance] * (questionB.answer in questionA.exp_answer)
            AsatisfiesB[1] += IMPORTANCE_POINTS[questionB.importance]
            BsatisfiesA[1] += IMPORTANCE_POINTS[questionA.importance]
        
        #Correction of the match score with the lower bound of uncertainty
        AsatisfiesB = AsatisfiesB[0] / AsatisfiesB[1]
        BsatisfiesA = BsatisfiesA[0] / BsatisfiesA[1]
        match_score = sqrt(AsatisfiesB * BsatisfiesA)
        match_score -= 1/len(S)
        if (match_score < 0) : match_score = 0
        
        return match_score
    
    def run(self, sorting=False):
        #Initializations
        matches_global = dict()
        for userA in self.users :
            matches_global[userA.iden] = []
        
        #all the match score computations between profiles
        for userA in self.users :
            for userB in self.users :
                
                if userA.iden < userB.iden :   #to not compute twice each score
                    match_score = self.get_match_score(userA, userB)
                    matches_global[userA.iden].append([userB.iden, match_score])
                    matches_global[userB.iden].append([userA.iden, match_score])
        
        
        #Sorting, another way, and selection of 10 bests
        for key, list_matches in matches_global.items():
            top10 = []
            for i in range(10):
                rankbest, matchbest = 0, list_matches[0]
                for rank, match in enumerate(list_matches):
                    if match[1] > matchbest[1]:
                        rankbest, matchbest = rank, match
                top10.append(matchbest)
                list_matches.pop(rankbest)

            matches_global[key] = top10 #conserve only the 10 bests
            
        return matches_global

if __name__ == '__main__':
    users = []
    
    print('reading input data...')
    with open('input.json') as json_file:  #reading input data
        data = json.load(json_file)
        
    for prof in data['profiles']: #transforming nested dicts and lists into objects
        iden = prof['id']
        questions = []
        for ans in prof['answers']:
            question = Question(ans['questionId'], 
                                ans['answer'],
                                ans['acceptableAnswers'], 
                                ans['importance'])
            questions.append(question)
        user = User(iden, questions)
        users.append(user)
       
    
    print('computing matches...')
    myOkcupid = Okcupid(users)
    matches_global = myOkcupid.run()
    
    
    print('writing output data...')
    res1 = []    #transforming the result's structure to the imposed output structure
    for prof, local_matches in matches_global.items():
        res2 = []
        for mtch in local_matches:
            temp1 = dict()
            temp1['profileId'], temp1['score'] = mtch[0], mtch[1]
            res2.append(temp1)
        temp2 = dict()
        temp2['profileId'], temp2['matches'] = prof, res2
        res1.append(temp2)
        
    matches_global = {'results' : res1}
    
    with open('output.json', 'w') as result:    #writing outut data
        result.write(json.dumps(matches_global, indent=4))
        
    print('The End')