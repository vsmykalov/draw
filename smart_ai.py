import tensorflow as tf
import numpy as np
import sys
import random
import time

from game import *



class AI(Strategy):
    def __init__(self, log=False):
        self.name = 'AI'
        self.clear()
        self.log = log

    def clear(self):
        self.X_hist = []
        self.D_hist = []
        self.Y_hist = []

    def make_move_X(self, g):
        assert g.turn == 1

        X_now = [0 for i in range(N * N * 3)]
        for i in range(N):
            for j in range(N):
                pos = i * N + j
                val = g.board[i][j]
                if val == 1:
                    X_now[pos] = 1
                if val == 2:
                    X_now[N + pos] = 1
                if val == -1:
                    X_now[N + N + pos] = 1

        D_now = [0 for i in range(N * N)]
        cnt_valid = 0
        for i in range(N):
            for j in range(N):
                pos = i * N + j
                if g.is_move_valid(i, j):
                    D_now[pos] = 1
                    cnt_valid += 1

        if not cnt_valid: return None

        probs = sess.run(A, feed_dict={X:np.array(X_now).reshape((N*N*3, 1)), D:np.array(D_now).reshape((N*N, 1))})

        if self.log:
            for i in range(N):
                for j in range(N):
                    print('%.3f' % probs[i * N + j][0], end=' ')
                print()
            print('-------------')

        rand = random.random()
        save_rnd = rand
        pos = -1
        while pos == -1:
            for i in range(N*N):
                rand -= probs[i][0]
                if rand <= 0 and D_now[i] > 0.5:
                    pos = i
                    break

        if pos == -1:
            print(D_now)
            #print(sess.run(Z_exp, feed_dict={X:np.array(X_now).reshape((N*N*3, 1)), D:np.array(D_now).reshape((N*N, 1))}))
            #print(sess.run(Z_drop, feed_dict={X:np.array(X_now).reshape((N*N*3, 1)), D:np.array(D_now).reshape((N*N, 1))}))
            print(probs)
            print(np.sum(probs))
            print(save_rnd)

        assert pos != -1

        x, y = (pos//N, pos%N)

        Y_now = [0 for i in range(N*N)]
        Y_now[pos] = 1

        self.X_hist.append(X_now)
        self.D_hist.append(D_now)
        self.Y_hist.append(Y_now)

        return (x, y)
    
    def make_move(self, g):
        if g.turn == 1:
            return self.make_move_X(g)
        else:
            g_inv = g.inv()
            move = self.make_move_X(g_inv)
            if not move: return None
            (x, y) = move
            (x, y) = (N - 1 - x, N - 1 - y)
            return (x, y)
            

W = tf.get_variable("W", shape=(N*N, N*N*3))
b = tf.get_variable("b", shape=(N*N, 1))

X = tf.placeholder(tf.float32, shape=(N*N*3, None))
D = tf.placeholder(tf.float32, shape=(N*N, None))

Y = tf.placeholder(tf.float32, shape=(N*N, None))
Y_weight = tf.placeholder(tf.float32, shape=(1, None))

Z = tf.add(tf.matmul(W, X), b)
Z_exp = tf.exp(Z)

Z_drop = tf.multiply(Z_exp, D)
A = tf.div(Z_drop, tf.reduce_sum(Z_drop, axis=0, keep_dims=True))

cost = tf.negative(tf.reduce_mean(tf.multiply(tf.reduce_sum(tf.multiply(tf.log(tf.maximum(A, 1e-9)), Y), axis=0, keep_dims=True), Y_weight)))


#optimizer = tf.train.MomentumOptimizer(0.001, 0.99).minimize(cost)
optimizer = tf.train.GradientDescentOptimizer(0.1).minimize(cost)
init = tf.global_variables_initializer()


saver = tf.train.Saver({"W":W, "b":b})
model_id = 6
restore_path = 'model/%d/500/model.ckpt' % model_id

import os
os.system('mkdir "model/%d"' % (model_id + 1))

games_in_stats = 1000

def train():
    global sess
    with tf.Session() as sess:
        sess.run(init)
        saver.restore(sess, restore_path)

        show_stats(AI(), HackedGreedyStrategy(), games_in_stats)

        iters = 10000
        games_per_iter = 1000

        average_time = 0
        sum_time = 0

        for it in range(iters):
            print('iter = %d, time to finish = %.2f secs' % (it, (iters - it) * average_time))

            start = time.time()
            
            all_X = []
            all_D = []
            all_Y = []
            all_Yw = []

            for game_id in range(games_per_iter):
                player1 = AI()
                player2 = AI()
        
                who_won = play_game(player1, player2)

                if False:
                    # case when both sides is AI
                    if who_won == 1:
                        Yw1 = [1 for i in player1.X_hist]
                        Yw2 = [-1 for i in player2.X_hist]
                    else:
                        Yw1 = [-1 for i in player1.X_hist]
                        Yw2 = [1 for i in player2.X_hist]
        
                    all_X += player1.X_hist
                    all_D += player1.D_hist
                    all_Y += player1.Y_hist
                    all_Yw += Yw1
                    
                    all_X += player2.X_hist
                    all_D += player2.D_hist
                    all_Y += player2.Y_hist
                    all_Yw += Yw2
                else:
                    # when only first side is AI
                    if who_won == 1:
                        Yw1 = [1 for i in player1.X_hist]
                    else:
                        Yw1 = [-1 for i in player1.X_hist]
        
                    all_X += player1.X_hist
                    all_D += player1.D_hist
                    all_Y += player1.Y_hist
                    all_Yw += Yw1
                    
        
            X_feed = np.array(all_X).T
            D_feed = np.array(all_D).T
            Y_feed = np.array(all_Y).T
            Yw_feed = np.array(all_Yw)
            Yw_feed = Yw_feed.reshape((1, len(all_Yw)))

            for i in range(10):
                sess.run(optimizer, feed_dict={X:X_feed, D:D_feed, Y:Y_feed, Y_weight:Yw_feed})
            
            end = time.time()

            sum_time += end - start
            average_time = sum_time / (it + 1)

            if (it + 1) % 10 == 0:
                saver.save(sess, 'model/%d/%d/model.ckpt' % (model_id + 1, it + 1))
                show_stats(AI(), HackedGreedyStrategy())
            if (it + 1) % 100 == 0:
                show_stats(AI(), HackedGreedyStrategy(), games_in_stats)



        player1 = AI()
        player2 = RandomStrategy()

        #show_stats(player1, player2, games_in_stats)
        show_game(player1, player2)


        saver.save(sess, 'model/%d/model.ckpt' % (model_id + 1))


def test():
    global sess
    with tf.Session() as sess:
        saver.restore(sess, restore_path)

        show_stats(AI(), HackedGreedyStrategy())
        #show_stats(AI(), RandomStrategy(), 10000)

if __name__ == "__main__":
    #test()
    train()
