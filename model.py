# The codes are modified from https://github.com/deepak112/Keras-SRGAN

from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import UpSampling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Conv2D, Conv2DTranspose
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LeakyReLU, PReLU
from tensorflow.keras.layers import add


# Residual block
def res_block_gen(model, kernal_size, filters, strides):

    gen = model
    model = Conv2D(filters = filters, kernel_size = kernal_size, strides = strides, padding = "same")(model)
    model = BatchNormalization(momentum = 0.5)(model)
    # Using Parametric ReLU
    model = PReLU(alpha_initializer='zeros', alpha_regularizer=None, alpha_constraint=None, shared_axes=[1,2])(model)
    model = Conv2D(filters = filters, kernel_size = kernal_size, strides = strides, padding = "same")(model)
    model = BatchNormalization(momentum = 0.5)(model)

    model = add([gen, model])

    return model

def discriminator_block(model, filters, kernel_size, strides):

    model = Conv2D(filters = filters, kernel_size = kernel_size, strides = strides, padding = "same")(model)
    model = BatchNormalization(momentum = 0.5)(model)
    model = LeakyReLU(alpha = 0.2)(model)

    return model

class Generator(object):

    def __init__(self, noise_shape):

        self.noise_shape = noise_shape

    def generator(self,output_ch):

	    gen_input = Input(shape = self.noise_shape)

	    model = Conv2D(filters = 64, kernel_size = (1,9), strides = 1, padding = "same")(gen_input)
	    model = PReLU(alpha_initializer='zeros', alpha_regularizer=None, alpha_constraint=None, shared_axes=[1,2])(model)

	    gen_model = model

        # Using 16 Residual Blocks
	    for index in range(16):
	        model = res_block_gen(model, (1,3), 64, 1)

	    model = Conv2D(filters = 64, kernel_size = (1,3), strides = 1, padding = "same")(model)
	    model = BatchNormalization(momentum = 0.5)(model)
	    model = add([gen_model, model])


	    model = Conv2D(filters = output_ch, kernel_size = (1,9), strides = 1, padding = "same")(model)
	    model = Activation('tanh')(model)

	    generator_model = Model(inputs = gen_input, outputs = model)

	    return generator_model

class Discriminator(object):

    def __init__(self, image_shape):

        self.image_shape = image_shape

    def discriminator(self):

        dis_input = Input(shape = self.image_shape)

        model = Conv2D(filters = 64, kernel_size = (1,3), strides = 1, padding = "same")(dis_input)
        model = LeakyReLU(alpha = 0.2)(model)

        model = discriminator_block(model, 64, (1,3), 2)
        model = discriminator_block(model, 128, (1,3), 1)
        model = discriminator_block(model, 128, (1,3), 2)
        model = discriminator_block(model, 256, (1,3), 1)
        model = discriminator_block(model, 256, (1,3), 2)
        model = discriminator_block(model, 512, (1,3), 1)
        model = discriminator_block(model, 512, (1,3), 2)

        model = Flatten()(model)
        model = Dense(1024)(model)
        model = LeakyReLU(alpha = 0.2)(model)

        model = Dense(1)(model)
        model = Activation('sigmoid')(model)

        discriminator_model = Model(inputs = dis_input, outputs = model)

        return discriminator_model
    