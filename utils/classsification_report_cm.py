def evaluate_model(model, test_loader, device, class_names):
    """
    Evaluate model and display confusion matrix and classification report.
    
    Args:
        model: PyTorch model to evaluate
        test_loader: DataLoader for test data
        device: Device to run evaluation on (cuda/cpu)
        class_names: List of class names for labels
    """
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix, classification_report
    import numpy as np
    import seaborn as sns
    import torch
    
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.xlabel("Predicted Labels")
    plt.ylabel("True Labels")
    plt.title("Confusion Matrix")
    plt.show()
    
    # Classification Report
    report = classification_report(all_labels, all_preds, target_names=class_names)
    print(report)
    
    return all_preds, all_labels

#example
#preds, labels = evaluate_model(model, test_loader, device, combined_classes)