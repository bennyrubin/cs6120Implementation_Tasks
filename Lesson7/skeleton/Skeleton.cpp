#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) { // for each function module
            for (auto &B : F) {
                for (auto &I : B) {
                    //errs() << "Instructions: " << I << "\n";
                    if (auto *instr = dyn_cast<BinaryOperator>(&I)) {
                        errs() << "Found return instruction" << instr << "\n";
                        if (instr->getOpcode() == Instruction::Add) {     
                            errs() << "It's an addition instruction." << '\n';

                            Value *lhs = instr->getOperand(0);
                            Value *rhs = instr->getOperand(1);

                            if (ConstantInt* CI = dyn_cast<ConstantInt>(rhs)) {
                                auto constInt = CI->getZExtValue();
                                errs() << "Value: " << constInt;
                                IRBuilder<> builder(instr);

                                Value *lhs = instr->getOperand(0);
                                Value *one = builder.getInt32(1);
                                Value *add = builder.CreateAdd(lhs,one);

                                for (int i = 0; i < constInt-1; i++) {
                                    add = builder.CreateAdd(add, one);
                                }

                                for (auto &U : instr->uses()) {
                                     User *user = U.getUser();
                                     user->setOperand(U.getOperandNo(), add);
                                }
                            } else if (ConstantInt* CI = dyn_cast<ConstantInt>(lhs)) {
                                auto constInt = CI->getZExtValue();
                                errs() << "Value: " << constInt;
                                IRBuilder<> builder(instr);

                                Value *rhs = instr->getOperand(1);
                                Value *one = builder.getInt32(1);
                                Value *add = builder.CreateAdd(one,rhs);

                                for (int i = 0; i < constInt-1; i++) {
                                    add = builder.CreateAdd(add, one);
                                }

                                for (auto &U : instr->uses()) {
                                     User *user = U.getUser();
                                     user->setOperand(U.getOperandNo(), add);
                                }
                            }

                            //errs() << "is a const: " << isa<ConstantInt>(rhs) << "for " << rhs << "\n";
                        }
                    }
                }
                for (auto &I : B) {
                    errs() << I << "\n";
                }
            }
        }

        return PreservedAnalyses::none(); //none means nothing is preserved
    };
};  

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Skeleton pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(SkeletonPass());
                });
        }
    };
}
