import tensorflow as tf

W = tf.constant([
    [.2, .3, -.1, -.2],
    [.2, -.1, .7, -.1],
    [.1, .4, -.4, -.3],
], dtype=tf.float32)
print(W.get_shape()) # (3, 4)

x = tf.constant([
        [0.0],
        [1.0],
        [2.0],
        [3.0]
    ]
)
print(x.get_shape()) # (1, 4)

a = tf.matmul(W,x)

print(tf.session(a))

