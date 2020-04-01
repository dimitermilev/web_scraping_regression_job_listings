from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import KFold
from sklearn import metrics
from regressors import stats    

def linear_regression_model(df, outcome):
    '''Function to fit simple linear regression to dataset, with parameter to specify outcome to learn against'''
    X = df.drop(outcome, axis=1)
    y = df[outcome]
    lr = LinearRegression()
    '''Split the data into sample and test sets'''
    X_sample, X_test, y_sample, y_test = train_test_split(X, y, test_size=0.2 )
    '''Split data into training and validation sets'''
    X_train, X_val, y_train, y_val = train_test_split(X_sample, y_sample, test_size=0.25)
    '''Fit the model against the training data'''
    lr.fit(X_train, y_train)
    '''Evaluate the model against the validation data'''
    print("R-squared score: ",lr.score(X_val, y_val))
    print("Intercept value: ",lr.intercept_)
    print("Feature coefficients:")
    for feature, coef in zip(X.columns, lr.coef_):
        print(feature, ':', f'{coef:.2f}') 

    '''Final model performance against the test data'''
    y_pred = lr.predict(X_test)
    res_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred}) 
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))  
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))  
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    return

def kfold_linear_regression_lasso_ridge(df, outcome):
    '''Function to fit ridge and lasso linear regression to dataset, with parameter to specify outcome to learn against'''
    X = df.drop(outcome, axis=1)
    y = df[outcome]
    '''Split the data into sample and test sets'''
    X_sample, X_test, y_sample, y_test = train_test_split(X, y, test_size=0.2 )
    '''Set up a 10 fold cross-validation structure'''
    kf = KFold(n_splits=10, shuffle=True, random_state = 1)

    '''Populate three lists with 3 models performance''' 
    cv_lm_r2s, cv_lm_reg_r2s, cv_lm_lasso_r2s= [], [], []
    for train_ind, val_ind in kf.split(X_sample,y_sample):
        X_train, y_train = X.iloc[train_ind], y.iloc[train_ind]
        X_val, y_val = X.iloc[val_ind], y.iloc[val_ind] 

        '''Simple Linear Regression'''
        lm = LinearRegression()
        lm.fit(X_train, y_train)
        cv_lm_r2s.append(lm.score(X_val, y_val))

        '''Feature scaling for Ridge and Lasso'''
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)

        '''Ridge Regression'''
        lm_reg = Ridge(alpha=10)
        lm_reg.fit(X_train_scaled, y_train)
        cv_lm_reg_r2s.append(lm_reg.score(X_val_scaled, y_val))

        '''Lasso Regression'''
        lm_lasso = Lasso(alpha=10)
        lm_lasso.fit(X_train_scaled, y_train)
        cv_lm_lasso_r2s.append(lm_lasso.score(X_val_scaled, y_val))
        
    '''Cross validation results for simple, Ridge, and Lasso regression'''
    print('Simple regression scores: ', cv_lm_r2s,'\n')
    print('Ridge scores: ', cv_lm_reg_r2s, '\n')
    print('Lasso scores: ', cv_lm_reg_r2s, '\n')
    print(f'Simple mean cv r^2: {np.mean(cv_lm_r2s):.3f} +- {np.std(cv_lm_r2s):.3f}')
    print(f'Ridge mean cv r^2: {np.mean(cv_lm_reg_r2s):.3f} +- {np.std(cv_lm_reg_r2s):.3f}')
    print(f'Lasso mean cv r^2: {np.mean(cv_lm_lasso_r2s):.3f} +- {np.std(cv_lm_lasso_r2s):.3f}')
    
    '''Model performance on test data'''
    y_pred = lm_reg.predict(X_test_scaled)
    res_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))  
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))  
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    return lm, lm_reg, lm_lasso
