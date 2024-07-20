import os

# turn of the tensorflow comments
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


import tensorflow as tf
from tensorflow import keras

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout

from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import TensorBoard

from matplotlib import pyplot as plt

import numpy as np
import time
import pickle
import math
from copy import deepcopy
from tools.logger import pickle_thisData_at
import logging
import subprocess as sub
import tarfile
import os

logger = logging.getLogger(__name__)


class NeuralNetwork(object):
    """A container for neural networks, data generated during the evolutionary search 
    is fed to NN, during evaluation time."""
    def __init__(self, args):
        self.args=args
        self.NN=None
        self.model_callbacks=None
        self.num_morphology_param=None
        self.num_magnetic_param=None
        self.best_model=None

        self.NN_run_on='cpu:0'

        self.NN_batch_size=args.NN_batch_size
        self.NN_epochs_num=args.NN_epochs_num
        self.NN_adaptive_epoch_num=False
        if args.NN_adaptive_epoch_num:
            self.NN_epochs_num=None
            self.NN_adaptive_epoch_num=True
        self.NN_shuffle= True if args.NN_shuffle else False
        self.NN_verbose=args.NN_verbose
        self.NN_validation_split=args.NN_validation_split
        self.NN_pop_test_split=args.NN_pop_test_split
        self.NN_sample_weights=True if args.NN_sample_weights else False
        self.NN_sample_weights_method=args.NN_sample_weights_method


        # dataset
        self.train_X=None
        self.train_Y=None
        self.train_sample_weights=None
        self.test_X=None
        self.test_Y=None

        self.history=None
        self.train_hist = []
        self.validation_hist = []
        self.test_hist = []
        self.test_MSE=999

        # prediction mse of the NN for the cases where NN is used for the next generation
        self.prediction_MSE=999
        self.prediction_errors = dict(prediction_error = [],
                                      generation_number = [],
                                      explore = [])

        self.data_process_type=args.NN_data_process_type

        # for adaptive epoch number selection with respect to the evaluation time
        self.NN_train_time_per_epoch=None
        self.evaluation_time_per_generation=None
        self.epoch_per_evaluation=1

        # save files
        self.NN_save_folder=args.run_directory+"/NNData"
        self.NN_save_files=dict(
                            raw_text=self.NN_save_folder+"/NN_raw_dataset_XY.txt",
                            raw_pickle=self.NN_save_folder+"/NN_raw_dataset_XY.pickle",
                            processed_pickle=self.NN_save_folder+"/NN_processed_dataset_XY.pickle",
                            training_model=self.NN_save_folder+"/model_training",
                            best_model=self.NN_save_folder+"/model_best",
                            checkpoint=self.NN_save_folder+"/checkpoint" ,
                            checkpoint_training_model=self.NN_save_folder+"/checkpoint/training_model_gen_",
                            checkpoint_best_model=self.NN_save_folder+"/checkpoint/best_model_gen_",
                            checkpoint_data = self.NN_save_folder+"/checkpoint/NNdata_gen_",
                            tensorboard_logs=self.NN_save_folder+"/logs",
                            warm_start_file=self.args.NN_warm_start_file
                            )

        self.model_callbacks=None
        self.load_callbacks()

        if args.NN_input_type == "1D_direct_morph_mag":
            self.num_morphology_param = int(np.prod(args.ind_size))
            #2x since we have Mtheta and Mphi variables for magnetic
            self.num_magnetic_param = int(2*np.prod([x/y for x, y in zip(args.ind_size, args.segment_size)]))
            input_dimension=self.num_morphology_param+self.num_magnetic_param
        else:
            raise NotImplementedError

        if not self.args.NN_warm_start:
            assert self.add_NN(args), "could not create the NN"
            self.best_model=self.NN


    def __iter__(self):
        """Iterate over the networks. Use the expression 'for n in network'."""
        return iter(self.NN)

    def __len__(self):
        """Return the number of networks in the genotype. Use the expression 'len(network)'."""
        return len(self.NN)

    def __getitem__(self):
        """Return network.  Use the expression 'network'."""
        return self.NN

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def add_NN(self, args):
        """Append a new network to this list of networks.

        Parameters
        ----------
        freeze : bool
            This indicator is used to prevent mutations to a network while freeze == True

        num_consecutive_mutations : int
            Uses this many (random) steps per mutation.

        """
        "create a sequential NN with using keras backend of tf"
        
        model = Sequential()

        # input dimension
        if args.NN_input_type == "1D_direct_morph_mag":
            self.num_morphology_param = int(np.prod(args.ind_size))
            #2x since we have Mtheta and Mphi variables for magnetic
            self.num_magnetic_param = int(2*np.prod([x/y for x, y in zip(args.ind_size, args.segment_size)]))
            input_dimension=self.num_morphology_param+self.num_magnetic_param
        else:
            raise NotImplementedError
        
        # get/arrange the NN layers
        NN_layers=[]
        if args.NN_layers is None:
            NN_layers=[]
            for i in range(args.NN_layer_num):
                NN_layers.append(args.NN_node_num)
        else:
            NN_layers=args.NN_layers

        # add the layers to the model

        # input layer
        model.add(Dense(NN_layers[0], 
                        input_dim=int(input_dimension), 
                        activation=args.NN_activation_function,
                        kernel_initializer='random_normal',
                        bias_initializer='ones'))
        model.add(Dropout(args.NN_dropout_ratio, input_shape=(NN_layers[0],)))
        NN_layers.pop(0)
        
        # add the other layers
        for node_num in NN_layers:
            model.add(Dense(node_num, 
                            activation=args.NN_activation_function, 
                            kernel_initializer='random_normal',
                            bias_initializer='ones'))
            model.add(Dropout(args.NN_dropout_ratio, input_shape=(node_num,)))

        # add the final layer, which does regression
        if args.fitness_calc_type == "positionMSE":
            model.add(Dense(1, 
                            activation='sigmoid', 
                            kernel_initializer='random_normal',
                            bias_initializer='ones'))
        else:

            model.add(Dense(1))
            model.add(keras.layers.LeakyReLU(alpha=0.1))


        # compile the keras model
        model.compile(loss=args.NN_loss, optimizer=args.NN_optimizer, metrics=[args.NN_metrics])
        model.summary()


        self.NN=model

        return 1

    def load_warm_start(self, warm_start_file, warm_start_model=None):

        if self.args.NN_warm_start_processedPrior:

            # data_file=warm_start_file+"/NN_dataset_XY.pickle"
            assert os.path.isfile(warm_start_file), "warm start data file does not exist"
            self.load_dataset(warm_start_file)

        else: 
            # check if it is a arranged txt or pickle file
            if warm_start_file.split(".")[-1] == "pickle":  
                assert os.path.isfile(warm_start_file), "warm start data file does not exist"
                with open(warm_start_file, 'rb') as f:
                    datasetXY = pickle.load(f)
                self.update_dataset(self.args, pop_individuals=None, data=datasetXY)
            else:
                # TODO:load from txt
                # TODO:process data organize it into the pickle format
                print("TODO: you have forgetten something here")



        # train the model with prior data
        best_model_file=warm_start_file+"/model_best"
        if os.path.isdir(best_model_file):
            self.NN=keras.models.load_model(best_model_file)
            self.best_model=self.NN
            self.train_NN(self.args, epoch_num=1)
        else:
            assert self.add_NN(self.args), "could not create the NN"
            self.best_model=self.NN
            self.train_NN(self.args, epoch_num=self.args.NN_warm_start_train_epoch)


    def draw_NN_learning_curve(self, dpiValue=150):
        filePath2save = self.args.run_directory + "/finalData/NN_learningCurve_MSE.jpg"
        # list all data in history
        # summarize history for accuracy
        fig = plt.figure(figsize=(10,5))
        plt.rcParams['font.size'] = 15
        gens = np.linspace(0, len(self.train_hist)-1, num=len(self.train_hist))
        plt.plot(gens, self.train_hist, linewidth=3)
        plt.plot(gens, self.test_hist, linewidth=3)
        if not self.NN_validation_split==-1:
            plt.plot(gens, self.validation_hist, linewidth=3)
            plt.legend(['train', 'test', 'validation'], loc='upper left')
        else:
            plt.legend(['train', 'test'], loc='upper left')
        plt.title('Model MSE')
        plt.ylabel('MSE')
        plt.xlabel('Generation #')
        fig.savefig(filePath2save, dpi=dpiValue)
        plt.close()


        filePath2save = self.args.run_directory + "/finalData/NN_learningCurve_mm.jpg"
        # list all data in history
        # summarize history for accuracy
        fig = plt.figure(figsize=(10,5))
        plt.rcParams['font.size'] = 15
        gens = np.linspace(0, len(self.train_hist)-1, num=len(self.train_hist))
        
        plt.plot(gens, self.args.ind_size[0]*self.args.lattice_dim*1e3*2*np.sqrt(self.train_hist), linewidth=3)
        plt.plot(gens, self.args.ind_size[0]*self.args.lattice_dim*1e3*2*np.sqrt(self.test_hist), linewidth=3)
        if not self.NN_validation_split==-1:
            plt.plot(gens, self.args.ind_size[0]*self.args.lattice_dim*1e3*2*np.sqrt(self.validation_hist), linewidth=3)
            plt.legend(['train', 'test', 'validation'], loc='upper left')
        else:
            plt.legend(['train', 'test'], loc='upper left')
        plt.title('Model mm')
        plt.ylabel('Estimation error (mm)')
        plt.xlabel('Generation #')
        fig.savefig(filePath2save, dpi=dpiValue)
        plt.close()


    def eval_NN(self, args, test_X=None, test_Y=None):
        # self.load_best_model()
        if test_Y is None:
            if self.test_Y is not None:
                test_X=self.test_X
                test_Y=self.test_Y
            else:
                raise NotImplementedError

        if args.NN_use_best_model:
            _, test_MSE = self.best_model.evaluate(test_X, test_Y, verbose=self.NN_verbose)
        else:
            _, test_MSE = self.NN.evaluate(test_X, test_Y, verbose=self.NN_verbose)

        if args.cluster_debug: print("NN evaluated")
        
        if self.args.debug: print('Test MSE: %f' % (test_MSE))
        if test_MSE<self.test_MSE:
            self.test_MSE=test_MSE


        self.test_hist.append(test_MSE)

        self.draw_NN_learning_curve()
        if args.cluster_debug: print("NN  learning curve updated and drawn")

        return test_MSE

    def train_NN(self, args, epoch_num=None, train_X=None, train_Y=None):
        if args.cluster_debug: print("starting NN train")
        if epoch_num is None:
            if self.NN_epochs_num is not None:
                epoch_num=self.NN_epochs_num
            elif self.NN_epochs_num is None and self.NN_adaptive_epoch_num:
                if self.NN_train_time_per_epoch is None or self.evaluation_time_per_generation is None:
                    epoch_num = 1
                else:
                    assert self.evaluation_time_per_generation is not None, "evaluation time per generation is required"
                    epoch_num = int(self.evaluation_time_per_generation/self.NN_train_time_per_epoch)
                    epoch_num=int((epoch_num-1)*0.7)   # consevative epoch number
                    if epoch_num<1:
                        epoch_num=1
                    if self.args.isCPUenabled: # preventing the epoch number to explode
                        if epoch_num>30:
                            epoch_num=30
                    
            else:
                raise NotImplementedError  
        if args.cluster_debug: print("epoch number is set")
        
        if train_Y is None:
            if self.train_Y is not None:
                train_X=self.train_X
                train_Y=self.train_Y
            else:
                raise NotImplementedError

        if self.NN_validation_split==-1:
            if self.test_Y is not None:
                starttime = time.time()

                self.history=self.NN.fit(train_X, train_Y, 
                                    validation_data=(self.test_X, self.test_Y), 
                                    shuffle=self.NN_shuffle, 
                                    epochs=epoch_num, 
                                    batch_size=self.NN_batch_size, 
                                    verbose=self.NN_verbose, 
                                    callbacks=self.model_callbacks,
                                    sample_weight=self.train_sample_weights)

                self.NN_train_time_per_epoch = (time.time()-starttime)/epoch_num
            else:
                raise NotImplementedError
        else:
            starttime = time.time()

            self.history=self.NN.fit(train_X, train_Y,
                                    validation_split=self.NN_validation_split, 
                                    shuffle=self.NN_shuffle, 
                                    epochs=epoch_num, 
                                    batch_size=self.NN_batch_size, 
                                    verbose=self.NN_verbose, 
                                    callbacks=self.model_callbacks)
            self.NN_train_time_per_epoch = (time.time()-starttime)/epoch_num

            self.validation_hist.append(sum(self.history.history['val_mean_squared_error'])/len(self.history.history['val_mean_squared_error']))

        self.train_hist.append(sum(self.history.history['mean_squared_error'])/len(self.history.history['mean_squared_error']))
        if args.cluster_debug: print("NN is trained")

        self.eval_NN(args)


    def save_at_checkpoint(self, generation):
        if not os.path.isdir(self.NN_save_files["checkpoint"]):
            sub.call("mkdir "+self.NN_save_folder+"/checkpoint" , shell=True)
        self.save_model()
        self.save_dataset(save_file=self.NN_save_files["processed_pickle"])
        # compress the pickled NN data, and models with generation label, 
        self.compress_NN_data(self.args, generation)
        self.erase_dataset()
        self.erase_model()
        self.erase_callbacks()

    def load_after_saving_at_checkpoint(self):
        # only for loading right after saving at the checkpointing. where the whole NN object is pickled
        self.load_model()
        self.load_callbacks()
        self.load_dataset()

    def load_at_checkpoint(self, generation):
        # continue from a checkpoint
        self.decompress_and_unpickle_NN_data(self.args, generation)
        self.load_model()
        self.load_callbacks()
        self.load_dataset()
        
    def save_model(self):
        self.NN.save(self.NN_save_files["training_model"])
        self.best_model.save(self.NN_save_files["best_model"])

    def erase_model(self):
        self.NN=None
        self.best_model=None
        self.history=None

    def load_model(self):
        self.NN=keras.models.load_model(self.NN_save_files["training_model"])
        self.best_model=keras.models.load_model(self.NN_save_files["best_model"])

    def load_best_model(self):
        self.best_model=keras.models.load_model(self.NN_save_files["best_model"])
          
    def erase_callbacks(self):
        self.model_callbacks=None    

    def load_callbacks(self):
        callbacks=None
        # create a callback if tensorboard is enabled
        if self.args.NN_tensorBoard_callback:
            cb_tb=TensorBoard(log_dir=self.NN_save_files["tensorboard_logs"])
            callbacks = [cb_tb]
        
        if self.args.NN_modelCheckpoint_callback:
            filepath = self.NN_save_files["best_model"]
               
            cb_checkpoint = ModelCheckpoint(filepath=filepath, 
                                        monitor="val_loss",
                                        verbose=1 if self.NN_verbose else 0, 
                                        save_best_only=True,
                                        mode="min")
            if callbacks is None:
                callbacks=[cb_checkpoint]
            else:
                callbacks.append(cb_checkpoint)

        self.model_callbacks=callbacks


    def process_X(self, args, X):
        X_processed = deepcopy(X)
        if self.data_process_type=="beam" or self.data_process_type=="sheet":
            # normalize within a range morphology (0, 1, ... ,N), Mtheta(0 -- pi), or Mphi(-pi -- pi) to (-1 -- 1)
            mag_param=int(self.num_magnetic_param/2)
            if not args.encoding_type == "multi_material":
                X_processed[:,:-2*mag_param]=(X_processed[:,:-2*mag_param]-0.5)*2
            else:
                X_processed[:,:-2*mag_param]=(X_processed[:,:-2*mag_param]-(args.material_num/2))/(args.material_num/2)

            X_processed[:,-2*mag_param:-mag_param]=X_processed[:,-2*mag_param:-mag_param]/math.pi
            X_processed[:,-mag_param:]=(X_processed[:,-mag_param:]-math.pi/2)/math.pi*2

        return X_processed


    def process_dataset(self, args, X, Y):

        processed_X = self.process_X(args, X)

        # process Y
        if self.data_process_type=="beam":
            if not args.fitness_maximize:

                # scale output to 0-1
                # set max error to twice of the beam length
                yMax=np.max(args.ind_size)*args.lattice_dim*1e3*2
                
                Y=Y/yMax
                Y=np.clip(Y, a_min=0, a_max=1)

            elif args.fitness_maximize:
                pass

        elif self.data_process_type=="sheet":
            pass

        processed_Y=Y
        return [processed_X, processed_Y]

    def compute_sample_weights(self, Y):
        weights=np.ones(Y.shape[0])
        if self.NN_sample_weights_method=="inverse":
            weights=1/Y
        elif self.NN_sample_weights_method=="inverse_clip":
            weights=1/Y
            weights=np.clip(weights,a_min=0.5,a_max=2)
        elif self.NN_sample_weights_method=="clip":
            weights=Y
            weights=np.clip(weights,a_min=0.5,a_max=2)
        elif self.NN_sample_weights_method=="no_weight":
            pass
        else:
            raise NotImplementedError
            
        return weights

    def update_dataset(self, args, pop_individuals=None, data=None):
        func_start_t = time.time()

        if data is None:
            # save raw data for this run
            if args.NN_save_raw_txt:

                if not os.path.isfile(self.NN_save_files["raw_text"]):
                    fileTXT = open(self.NN_save_files["raw_text"], "w")
                elif os.path.isfile(self.NN_save_files["raw_text"]):
                    fileTXT = open(self.NN_save_files["raw_text"], "a")
                else:
                    raise NotImplementedError

            X=None
            Y=None

            for ind in pop_individuals:
                
                # get the data
                id = ind.id
                voxel_map = ind.designParameters["material"]
                Mtheta = ind.segmentedMprofile["Mtheta"]
                Mphi = ind.segmentedMprofile["Mphi"]
                fitness = ind.fitness

                voxel_map1D = voxel_map.flatten()
                Mtheta1D = Mtheta.flatten()
                Mphi1D= Mphi.flatten()

                if args.NN_save_raw_txt:
                    # write it into .txt file
                    fileTXT.write(str(id)+";")
                    np.savetxt(fileTXT, [voxel_map1D], delimiter=',', fmt='%-2.5f', newline="")
                    fileTXT.write(";")
                    np.savetxt(fileTXT, [Mtheta1D], delimiter=',', fmt='%-2.5f',newline="")
                    fileTXT.write(";")
                    np.savetxt(fileTXT, [Mphi1D], delimiter=',', fmt='%-2.5f',newline="")
                    fileTXT.write(";")
                    fileTXT.write(str(fitness)+";\n")

                # arrange the pickle data
                x=np.concatenate((voxel_map1D,Mtheta1D, Mphi1D))
                y=fitness
                if X is None:
                    X=x
                    Y=y
                else:
                    X=np.vstack((X,x))
                    Y=np.vstack((Y,y))
                
            if args.NN_save_raw_txt:
                fileTXT.close()

            if args.NN_save_raw_pickle:
                pickle_file=self.NN_save_files["raw_pickle"]
                if not os.path.isfile(pickle_file):
                    dataset= dict(X=X,
                                Y=Y)
                    
                elif os.path.isfile(pickle_file):
                    with open(pickle_file, 'rb') as f:
                        dataset = pickle.load(f)
                        Xraw=dataset['X']
                        Yraw=dataset['Y']

                    Xraw=np.vstack((Xraw,X))
                    Yraw=np.vstack((Yraw,Y))
                    dataset= dict(X=Xraw,
                                Y=Yraw)

                pickle_thisData_at(dataset, pickle_file)

        else:
            if self.args.NN_warm_start:
                X=data['X']
                Y=data['Y']
            else:
                raise NotImplementedError

        # process the data -- could be normalization or any other pre-process on the data
        processed_data=self.process_dataset(args, X, Y)
        X_processed=processed_data[0]
        Y_processed=processed_data[1]

        # update train and test datasets
        # randomly seperate it into train and test data
        test_ratio = self.NN_pop_test_split
        data_num = np.prod(Y.shape[0])
        test_data_num = int(test_ratio*data_num)
        if test_data_num == 0:  # making sure there is a test data, only for debugging purposes when the data number is really small
            test_data_num = 1

        # random pick train and test set --> it is shuffled before at the main algorithm flow due to repetability issues regarding random states
        train_data_num = data_num - test_data_num
        # Generate indices for training and testing sets
        train_indices = list(range(train_data_num))
        test_indices = list(set(range(data_num)) - set(train_indices))
        

        # update
        self.train_X=np.concatenate((self.train_X, X_processed[train_indices, :])) if self.train_X is not None else X_processed[train_indices, :]
        self.train_Y=np.concatenate((self.train_Y, Y_processed[train_indices, :])) if self.train_Y is not None else Y_processed[train_indices, :]
        self.test_X=np.concatenate((self.test_X, X_processed[test_indices, :])) if self.test_X is not None else X_processed[test_indices, :]
        self.test_Y=np.concatenate((self.test_Y, Y_processed[test_indices, :])) if self.test_Y is not None else Y_processed[test_indices, :]

        # update sample weights for the train
        if self.NN_sample_weights:
            sample_weights=self.compute_sample_weights(Y[train_indices, :])
            self.train_sample_weights=np.concatenate((self.train_sample_weights, sample_weights)) if self.train_sample_weights is not None else sample_weights

        func_end_t = time.time() - func_start_t
        if args.debug: print("Total time to update NN dataset: ", func_end_t)


    def save_dataset(self, save_file):
        dataset= dict(trainX=self.train_X,
                        trainY=self.train_Y,
                        trainSampleWeights=self.train_sample_weights,
                        testX=self.test_X,
                        testY=self.test_Y)

        with open(save_file, "wb") as handle:
            pickle.dump(dataset, handle)
    
    def load_dataset(self, load_file=None):
        if load_file==None:
            load_file=self.NN_save_files["processed_pickle"]
        
        with open(load_file, 'rb') as f:
            dataset = pickle.load(f)

        self.train_X=dataset["trainX"]
        self.train_Y=dataset["trainY"]
        self.train_sample_weights=dataset["trainSampleWeights"]
        self.test_X=dataset["testX"]
        self.test_Y=dataset["testY"]

    def erase_dataset(self):
        # dataset
        self.train_X=None
        self.train_Y=None
        self.train_sample_weights=None
        self.test_X=None
        self.test_Y=None


    def update_prediction_error(self, pop):
        if self.args.cluster_debug: print("updating the prediction error")
        if self.args.cluster_debug: print("pop robot num: " + str(len(pop)))
        self.prediction_MSE=0
        for robot in pop:
            MSE = (robot.fitness-robot.fitness_prediction)**2
            self.prediction_MSE += MSE
        self.prediction_MSE= self.prediction_MSE / len(pop)
        self.prediction_errors["prediction_error"].append(math.sqrt(self.prediction_MSE))
        self.prediction_errors["generation_number"].append(pop.gen)
        self.prediction_errors["explore"].append(pop.explore)
        if self.args.cluster_debug: print("prediction error updated")


    # for NN predictions || psuedo simulation
    def convert_robot_params_to_x_predict(self, robot):
        for name, details in robot.genotype.to_phenotype_mapping.items():
            new = details["state"]
            if name=="material":
                voxel_map=new
            if name=="Mtheta":
                Mtheta=new
            if name=="Mphi":
                Mphi=new 
        voxel_map1D = voxel_map.flatten()
        Mtheta1D = Mtheta.flatten()
        Mphi1D= Mphi.flatten()
        x=np.concatenate((voxel_map1D, Mtheta1D, Mphi1D))
        X = x.reshape(1, x.size)
        X_predict = self.process_X(self.args, X)
        return X_predict

    def get_y_predicted(self, X_predict):

        if self.args.NN_use_best_model:
            y_predict=self.best_model(X_predict).numpy()
        else:
            y_predict=self.NN(X_predict).numpy()
       
        return y_predict

    def process_y_predict_to_fitness(self, y_predict):
        if self.args.NN_data_process_type == "beam":
            if not self.args.fitness_maximize:
                predicted_fitness=y_predict[0]*np.max(self.args.ind_size)*self.args.lattice_dim*1e3*2
            else:
                predicted_fitness=y_predict[0]

        elif self.args.NN_data_process_type=="sheet":
            predicted_fitness = y_predict[0]
        else:
            raise NotImplementedError
        
        return predicted_fitness

    # checkpoint operations on NN
    def compress_NN_data(self, args, generation):
        # compress the dataset with generation label
        file_path = self.NN_save_files["checkpoint_data"] +str(generation)+".tar.gz"
        
        with tarfile.open(file_path, 'w:gz') as archive:
            archive.add(self.NN_save_files["processed_pickle"], arcname="NN_processed_dataset_XY.pickle")

        # compress the training model with generation label
        file_path = self.NN_save_files["checkpoint_training_model"] +str(generation)+".tar.gz"

        with tarfile.open(file_path, 'w:gz') as archive:
            archive.add(self.NN_save_files["training_model"], arcname='.')

        # compress the best model with generation label
        file_path = self.NN_save_files["checkpoint_best_model"] +str(generation)+".tar.gz"

        with tarfile.open(file_path, 'w:gz') as archive:
            archive.add(self.NN_save_files["best_model"], arcname='.')

    def decompress_and_unpickle_NN_data(self, args, generation):
        # erase the leftover
        sub.call("rm "+self.NN_save_files["processed_pickle"], shell=True)
        sub.call("rm -r "+self.NN_save_files["training_model"]+"/*", shell=True)
        sub.call("rm -r "+self.NN_save_files["best_model"]+"/*", shell=True)

        # load it all
        path_to_extract = self.NN_save_folder
        file_path = self.NN_save_files["checkpoint_data"] +str(generation)+".tar.gz"
        with tarfile.open(file_path, 'r') as archive:
            archive.extractall(path_to_extract)

        path_to_extract = self.NN_save_files["training_model"]
        file_path = self.NN_save_files["checkpoint_training_model"] +str(generation)+".tar.gz"
        with tarfile.open(file_path, 'r') as archive:
            archive.extractall(path_to_extract)
        
        path_to_extract = self.NN_save_files["best_model"]
        file_path = self.NN_save_files["checkpoint_best_model"] +str(generation)+".tar.gz"
        with tarfile.open(file_path, 'r') as archive:
            archive.extractall(path_to_extract)

    
