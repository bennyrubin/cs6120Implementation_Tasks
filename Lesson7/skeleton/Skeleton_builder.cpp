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
                    errs() << "Instructions: " << I << "\n";
                    if (auto *op = dyn_cast<BinaryOperator>(&I)) {
                        IRBuilder<> builder(op);

                        Value *lhs = op->getOperand(0);
                        Value *rhs = op->getOperand(1);
                        Value *mul = builder.CreateMul(lhs,rhs);

                        for (auto &U : op->uses()) {
                            User *user = U.getUser();
                            user->setOperand(U.getOperandNo(), mul);
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
