
import numpy
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split


import Prob_MoE as pm
import utils as ut
import uframe as uf

if __name__ == "main":
    
    dataset = "california"
    result_path = r"D:\Github_Projects\MOE_Training_under_Uncertainty"
    # load data
    data, target, input_size, output_size = ut.preprocess_data(dataset = dataset)

    
    size = 200
    data_sc = MinMaxScaler().fit_transform(data[:size])
    target = target[:size]
    
    # split
    data_train, data_test, target_train, target_test = train_test_split(data_sc, target, test_size=0.2, random_state=42)
    # val
    data_train, data_val, target_train, target_val = train_test_split(data_train, target_train, test_size=0.25, random_state=42)   
    
    ############################ MoE #############################################################
    
    result_path = result_path + "\MoE"

    #uncertainty in data 
    X_train = uf.uframe_from_array_mice_2(data_train, kernel = "gaussian" , p =.2, mice_iterations = 2)
    X_val = uf.uframe_from_array_mice_2(data_val, kernel = "gaussian" , p =.2, mice_iterations = 2)
    # X.analysis(X_train, save= "filename", bins = 20)

    

    # MoE
    moe = pm.MoE(2, inputsize = input_size, outputsize = output_size)
    # val
    moe.fit(X_train, target_train, X_val, target_val, threshold_samples=0.8, local_mode = True, weighted_experts=True, 
            verbose=True, batch_size_experts=4, batch_size_gate=4, n_epochs=80, n_samples=400, lr = 0.01, reg_lambda=0.002, reg_alpha = 0.8)
  
    # predictions / eval
    predictions = moe.predict(data_test)
    score = moe.evaluation(predictions, target_test)
    print(f"score: {score}")
    
    moe.analyze(data_train, save_path = result_path)
    
    
    
    ############################ Referenz MoE #############################################################
    
    result_path = result_path + "\Ref_MoE"
    ref_train = uf.uframe()
    ref_train.append(X_train.mode())   
    
    
    # Ref MoE
    ref_moe = pm.MoE(2, inputsize = input_size, outputsize = output_size)
    # val
    ref_moe.fit(ref_train, target_train, X_val, target_val, threshold_samples=1, local_mode = False, weighted_experts = False, 
            verbose=True, batch_size_experts=5, batch_size_gate=5, n_epochs=20, n_samples=1, reg_lambda=0.0005, reg_alpha = 0.8)
  
    # predictions / eval
    predictions_ref = ref_moe.predict(data_test)
    score = ref_moe.evaluation(predictions_ref, target_test)
    print(f"Ref MoE score: {score}")
    
    ref_moe.analyze(data_train, save_path = result_path)
    
    
    ############################ Referenz NN #############################################################

    result_path = result_path + "\Ref_NN"
    ref_train = uf.uframe()
    ref_train.append(X_train.mode())   
    
    
    # NN
    nn = pm.MoE(1, inputsize = input_size, outputsize = output_size, hidden_experts = [64, 64, 64],  hidden_gate=[1])
    # val
    nn.fit(ref_train, target_train, X_val, target_val, threshold_samples=1, local_mode = False, weighted_experts = False, 
            verbose=True, batch_size_experts=5, batch_size_gate=5, n_epochs=20, n_samples=1, reg_lambda=0.0005, reg_alpha = 0.8)
  
    # predictions / eval
    predictions_ref = nn.predict(data_test)
    score = nn.evaluation(predictions_ref, target_test)
    print(f"Ref NN score: {score}")
    



        





