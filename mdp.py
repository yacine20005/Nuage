import CryptContext
password_ctx = CryptContext(schemes=["bcrypt"])

hash_pw = password_ctx.hash("Yacine05mdp") #Calcul du hash du mot de passe à stocker
password_ctx.verify("Yacine05mdp", hash_pw) #Vérification du mot de passe
