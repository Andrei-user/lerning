#!/usr/bin/env python3

import sys
import math

from geometry_msgs.msg import Twist

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from tf2_ros.transform_listener import TransformListener
from tf2_ros.buffer import Buffer
from tf2_ros import LookupException

class TfListener(Node):

    def __init__(self, first_turtle, second_turtle):
        super().__init__('tf_listener')
        self.first_name_ = first_turtle  # Имя первого объекта
        self.second_name_ = second_turtle  # Имя второго объекта
        self.get_logger().info("Transforming from {} to {}".format(self.second_name_, self.first_name_))  # Логгирование
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)  # Создание слушателя топиков TF
        self.cmd_ = Twist()  # Инициализация сообщения Twist для публикации управляющих команд
        self.publisher_ = self.create_publisher(Twist, "{}/cmd_vel".format(self.second_name_), 10)  # Создание издателя для публикации команд управления
        self.timer = self.create_timer(0.33, self.timer_callback)  # Создание таймера для вызова функции обратного вызова с заданной частотой (30 Hz)

    def timer_callback(self):
        try:
            # Получение преобразования между двумя объектами
            trans = self._tf_buffer.lookup_transform(self.second_name_, self.first_name_, rclpy.time.Time())
            # Вычисление линейной скорости
            self.cmd_.linear.x = math.sqrt(trans.transform.translation.x ** 2 + trans.transform.translation.y ** 2)
            # Вычисление угловой скорости
            self.cmd_.angular.z = 4 * math.atan2(trans.transform.translation.y, trans.transform.translation.x)
            # Публикация команды управления
            self.publisher_.publish(self.cmd_)
        except LookupException as e:
            # Обработка исключения, если не удалось получить преобразование
            self.get_logger().error('failed to get transform {} \n'.format(repr(e)))

def main(argv=sys.argv):
    rclpy.init(args=argv)  # Инициализация ROS
    # Создание узла и передача имен топиков в качестве аргументов
    node = TfListener(sys.argv[1], sys.argv[2])
    try:
        rclpy.spin(node)  # Запуск цикла обработки сообщений ROS
    except KeyboardInterrupt:
        pass
    node.destroy_node()  # Закрытие узла
    rclpy.shutdown()  # Завершение работы ROS

if __name__ == "__main__":
    main()  # Вызов функции main() при запуске скрипта
