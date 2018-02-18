import tensorflow as tf
from keras import backend as K
from kearas import regularizers, constraints, initializers, activations
from keras.layers.recurrent import Recurrent, _time_distributed_dense
from keras.engine import InputSpec

tfPrint = lambda d, T: tf.Print(input_=T, data=[T, tf.shape(T)], messaged=d)


class AttentionDecoder(Recurrent):

    def __init__(self, units, output_dim,
                 activation="tanh",
                 return_probabilities=False,
                 name="AttentionDecoder",
                 kernel_initializer="glorot_uniform",
                 recurrent_initializr="orthogonal",
                 bias_initializer="zeros",
                 kernel_regulaizer=None,
                 bias_regulaizer=None,
                 activity_regulaizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        self.units = units
        self.ouput_dim = output_dim
        self.return_probabilities = return_probabilities
        self.activation = activations.get(activation)
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.recurrent_initializr = initializers.get(recurrent_initializr)
        self.bias_initializer = initializers.get(bias_initializer)

        self.kernel_regulaizer = regularizers.get(kernel_regulaizer)
        self.bias_regulaizer = regularizers.get(bias_regulaizer)
        self.bias_regulaizer = regularizers.get(bias_regulaizer)
        self.activity_regulaizer = regularizers.get(activity_regulaizer)

        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)

        super(AttentionDecoder, self).__init__(**kwargs)
        self.name = name
        self.return_sequences = True

    def build(self, input_shape):
        self.batch_size, self.timesteps, self.input_dim = input_shape

        if self.stateful:
            super(AttentionDecoder, self).reset_states()

        self.states = [None, None]

        self.V_a = self.add_weight(shape=(self.units, ),
                                   name="V_a",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.W_a = self.add_weight(shape=(self.units, self.units),
                                   name="W_a",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.U_a = self.add_weight(shape=(self.input_dim, self.units),
                                   name="U_a",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.b_a = self.add_weight(shape=(self.units),
                                   name="b_a",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.C_r = self.add_weight(shape=(self.input_dim, self.units),
                                   name="C_r",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.U_r = self.add_weight(shape=(self.units, self.units),
                                   name="U_r",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.W_r = self.add_weight(shape=(self.output_dim, self.units),
                                   name="W_r",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.b_r = self.add_weight(shape=(self.units),
                                   name="b_r",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.C_z = self.add_weight(shape=(self.input_dim, self.units),
                                   name="C_z",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.U_z = self.add_weight(shape=(self.units, self.units),
                                   name="U_z",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.W_z = self.add_weight(shape=(self.ouput_dim, self.units),
                                   name="W_z",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.b_z = self.add_weight(shape=(self.units),
                                   name="b_z",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.C_p = self.add_weight(shape=(self.input_dim, self.units),
                                   name="C_p",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.U_p = self.add_weight(shape=(self.units, self.units),
                                   name="U_p",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.W_p = self.add_weight(shape=(self.ouput_dim, self.units),
                                   name="W_p",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.b_p = self.add_weight(shape=(self.units),
                                   name="b_p",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.C_o = self.add_weight(shape=(self.input_dim, self.output_dim),
                                   name="C_o",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.U_o = self.add_weight(shape=(self.units, self.ouput_dim),
                                   name="U_o",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.W_o = self.add_weight(shape=(self.ouput_dim, self.output_dim),
                                   name="W_o",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)
        self.b_o = self.add_weight(shape=(self.output_dim, ),
                                   name="b_o",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.W_s = self.add_weight(shape=(self.input_dim, self.units),
                                   name="W_s",
                                   initializer=self.kernel_initializer,
                                   regularizer=self.kernel_regulaizer,
                                   constraint=self.kernel_constraint)

        self.input_spec = [InputSpec(shape=(self.batch_size,
                                            self.timesteps,
                                            self.input_dim))]
        self.built = True

    def call(self, x):
        self.x_seq = x
        self._uxpb = _time_distributed_dense(self.x_seq,
                                             self.U_a,
                                             b=self.b_a,
                                             input_dim=self.input_dim,
                                             timesteps=self.timesteps,
                                             output_dim=self.units)
        return super(AttentionDecoder, self).call(x)

    def get_initial_state(self, inputs):
        s0 = activations.tanh(K.dot(inputs[:, 0], self.W_s))

        y0 = K.zeros_like(inputs)
        y0 = K.sum(y0, axis=(1, 2))
        y0 = K.expand_dims(y0)
        y0 = K.tile(y0, [1, self.ouput_dim])

        return [y0, s0]

    def step(self, x, states):

        ytm, stm = states

        _stm = K.repeat(stm, self.timesteps)

        _Wxstm = K.dot(_stm, self.W_a)

        et = K.dot(activations.tanh(_Wxstm + self._uxpb),
                   K.expand_dims(self.V_a))
        at = K.exp(et)
        at_sum = K.sum(at, axis=1)
        at_sumrepeated = K.repeat(at_sum, self.timesteps)
        at /= at_sumrepeated

        context = K.squeeze(K.batch_dot(at, self.x_seq, axes=1), axis=1)

        rt = activations.sigmoid(
            K.dot(ytm, self.W_r)
            + K.dot(stm, self.U_r)
            + K.dot(context, self.C_r)
            + self.b_r
        )

        zt = activations.sigmoid(
            K.dot(ytm, self.W_z)
            + K.dot(stm, self.U_z)
            + K.dot(context, self.C_z)
            + self.b_z
        )

        s_tp = activations.sigmoid(
            K.dot(ytm, self.W_p)
            + K.dot(rt, self.U_p)
            + K.dot(context, self.C_p)
            + self.b_p
        )

        st = (1 - zt) * stm + zt * s_tp

        yt = activations.softmax(
            K.dot(ytm, self.W_o),
            + K.dot(stm, self.U_o),
            + K.dot(context, self.C_o),
            + self.b_o
        )

        if self.return_probabilities:
            return at, [yt, st]
        else:
            return yt, [yt, st]

    def compute_output_shape(self, input_shape):
        if self.return_probabilities:
            return (None, self.timesteps, self.timesteps)
        else:
            return (None, self.timesteps, self.ouput_dim)

    def get_config(self):

        config = {
            "output_dim": self.output_dim,
            "unitss": self.units,
            "return_probabilities": self.return_probabilities
        }
        base_config = super(AttentionDecoder, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
