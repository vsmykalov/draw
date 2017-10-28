import tensorflow as tf
from game import N

W = tf.get_variable("W", shape=(N*N, N*N*3), initializer=tf.zeros_initializer)
b = tf.get_variable("b", shape=(N*N, 1), initializer=tf.zeros_initializer)

saver = tf.train.Saver()

with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)
    saver.save(sess, 'model/0/model.ckpt')