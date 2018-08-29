# Copyright chaye. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
import numpy as np
import tensorflow as tf
#import tensorflow.contrib.eager as tfe
#tfe.enable_eager_execution()
from thisalexnet import alexnet
from datagenerator import ImageDataGenerator
from datetime import datetime
import glob
from tensorflow.data import Iterator


def main():
    # 初始参数设置
    learning_rate = 1e-4
    num_epochs = 3  # 代的个数 之前是100
    batch_size = 50 # 之前是1024
    dropout_rate = 0.5
    num_classes = 2  # 类别标签
    display_step = 2 # display_step个batch_size训练完了就在tensorboard中写入loss和accuracy
                     # need: display_step <= train_dataset_size / batch_size

    filewriter_path = "./tmp/tensorboard"  # 存储tensorboard文件
    checkpoint_path = "./tmp/checkpoints"  # 训练好的模型和参数存放目录

    image_format = 'jpg' # 数据集的数据类型
    file_name_of_class = ['cat','dog'] # cat对应标签0,dog对应标签1。默认图片包含独特的名词，比如类别
    train_dataset_paths = ['G:/信抗实验室/Data_sets/catanddog/train/cat/', 
                           'G:/信抗实验室/Data_sets/catanddog/train/dog/'] # 指定训练集数据路径（根据实际情况指定训练数据集的路径）
    test_dataset_paths = ['G:/信抗实验室/Data_sets/catanddog/test/cat/',
                          'G:/信抗实验室/Data_sets/catanddog/test/dog/'] # 指定测试集数据路径（根据实际情况指定测试数据集的路径）
    # 初始参数设置完毕
        

    # 训练数据集数据处理
    train_image_paths = []
    train_labels = []
    # 打开训练数据集目录，读取全部图片，生成图片路径列表
    for train_dataset_path in train_dataset_paths:
        length = len(train_image_paths)
        train_image_paths[length:length] = np.array(glob.glob(train_dataset_path + '*.' + image_format)).tolist()
    for image_path in train_image_paths:
        image_file_name = image_path.split('/')[-1]
        for i in range(num_classes):
            if file_name_of_class[i] in image_file_name:
                train_labels.append(i)
                break

    # 测试数据集数据处理
    test_image_paths = []
    test_labels = []
    # 打开测试数据集目录，读取全部图片，生成图片路径列表
    for test_dataset_path in test_dataset_paths:
        length = len(test_image_paths)
        test_image_paths[length:length] = np.array(glob.glob(test_dataset_path + '*.' + image_format)).tolist()
    for image_path in test_image_paths:
        image_file_name = image_path.split('/')[-1]
        for i in range(num_classes):
            if file_name_of_class[i] in image_file_name:
                test_labels.append(i)
                break

    # get Datasets
    # 调用图片生成器，把训练集图片转换成三维数组
    train_data = ImageDataGenerator(
        images=train_image_paths,
        labels=train_labels,
        batch_size=batch_size,
        num_classes=num_classes,
        image_format=image_format,
        shuffle=True)

    # 调用图片生成器，把测试集图片转换成三维数组
    test_data = ImageDataGenerator(
        images=test_image_paths,
        labels=test_labels,
        batch_size=batch_size,
        num_classes=num_classes,
        image_format=image_format,
        shuffle=False)

    # get Iterators
    with tf.name_scope('input'):
        # 定义迭代器
        iterator = Iterator.from_structure(train_data.data.output_types,
                                       train_data.data.output_shapes)
        training_initalizer=iterator.make_initializer(train_data.data)
        testing_initalizer=iterator.make_initializer(test_data.data)
        # 定义每次迭代的数据
        next_batch = iterator.get_next()

    x = tf.placeholder(tf.float32, [batch_size, 227, 227, 3])
    y = tf.placeholder(tf.float32, [batch_size, num_classes])
    keep_prob = tf.placeholder(tf.float32)

    # 图片数据通过AlexNet网络处理
    fc8 = alexnet(x, keep_prob, num_classes)

    # loss
    with tf.name_scope('loss'):    
        loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=fc8,
                                                                  labels=y))
    # optimizer
    with tf.name_scope('optimizer'):      
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(loss_op)

    # accuracy
    with tf.name_scope("accuracy"):
        correct_pred = tf.equal(tf.argmax(fc8, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    init = tf.global_variables_initializer()

    # 把精确度加入到Tensorboard
    tf.summary.scalar('loss', loss_op)
    tf.summary.scalar('accuracy', accuracy)
    merged_summary = tf.summary.merge_all()
    writer = tf.summary.FileWriter(filewriter_path)

    # saver
    saver = tf.train.Saver()

    # 定义一代的迭代次数
    train_batches_per_epoch = int(np.floor(tr_data.data_size / batch_size))
    test_batches_per_epoch = int(np.floor(test_data.data_size / batch_size))

    # 开始训练
    with tf.Session() as sess:
        sess.run(init)

        # 把模型图加入Tensorboard
        writer.add_graph(sess.graph)

        print("{} Start training...".format(datetime.now()))
        print("{} Open Tensorboard at --logdir {}".format(datetime.now(),
                                                          filewriter_path))

        # 总共训练10代
        for epoch in range(num_epochs):
            sess.run(training_initalize)
            print("{} Epoch number: {} start".format(datetime.now(), epoch + 1))

            #开始训练每一代
            for step in range(train_batches_per_epoch):
                img_batch, label_batch = sess.run(next_batch)
                print('label_batch',sess.run(label_batch))
                sess.run(train_op, feed_dict={x: img_batch,
                                               y: label_batch,
                                               keep_prob: dropout_rate})
                if step % display_step == 0:
                    print('asdad')
                    s = sess.run(merged_summary, feed_dict={x: img_batch,
                                                            y: label_batch,
                                                            keep_prob: 1.})

                    writer.add_summary(s, epoch * train_batches_per_epoch + step)

            # 测试模型精确度
            print("{} Start validation".format(datetime.now()))
            sess.run(testing_initalize)
            test_acc = 0.
            test_count = 0

            for _ in range(test_batches_per_epoch):
                img_batch, label_batch = sess.run(next_batch)
                acc = sess.run(accuracy, feed_dict={x: img_batch,
                                                    y: label_batch,
                                                    keep_prob: 1.0})
                test_acc += acc
                test_count += 1

            test_acc /= test_count

            print("{} Validation Accuracy = {:.4f}".format(datetime.now(), test_acc))

            # 把训练好的模型存储起来
            print("{} Saving checkpoint of model...".format(datetime.now()))

            checkpoint_name = os.path.join(checkpoint_path, 'model_epoch' + str(epoch + 1) + '.ckpt')
            save_path = saver.save(sess, checkpoint_name)

            print("{} Epoch number: {} end".format(datetime.now(), epoch + 1))


if __name__ == '__main__':
    main()